from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Deploiement, Journal
from .serializers import DeploiementSerializer, JournalSerializer


class DeploiementViewSet(viewsets.ModelViewSet):
    serializer_class = DeploiementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['statut', 'commit_hash', 'projet__nom']
    ordering_fields = ['date_heure', 'statut']
    ordering = ['-date_heure']

    def get_queryset(self):
        return Deploiement.objects.filter(
            projet__proprietaire=self.request.user
        ).order_by('-date_heure')

    def perform_create(self, serializer):
        serializer.save(statut=Deploiement.Statut.EN_ATTENTE)

    @action(detail=True, methods=['post'])
    def lancer(self, request, pk=None):
        """Lance un déploiement en attente"""
        deploiement = self.get_object()

        if deploiement.statut != Deploiement.Statut.EN_ATTENTE:
            return Response(
                {'error': f"Impossible de lancer un déploiement avec le statut '{deploiement.statut}'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        deploiement.statut = Deploiement.Statut.EN_COURS
        deploiement.save()

        Journal.objects.create(
            deploiement=deploiement,
            niveau=Journal.Niveau.INFO,
            message=f"Déploiement #{deploiement.id} lancé pour le projet '{deploiement.projet.nom}'",
            source='system'
        )

        return Response({
            'message': f"Déploiement #{deploiement.id} lancé avec succès",
            'statut': deploiement.statut,
        })

    @action(detail=True, methods=['post'])
    def terminer(self, request, pk=None):
        """Marque un déploiement comme réussi ou échoué"""
        deploiement = self.get_object()

        if deploiement.statut != Deploiement.Statut.EN_COURS:
            return Response(
                {'error': "Le déploiement n'est pas en cours"},
                status=status.HTTP_400_BAD_REQUEST
            )

        nouveau_statut = request.data.get('statut')
        if nouveau_statut not in ['SUCCES', 'ECHEC']:
            return Response(
                {'error': "Statut invalide. Choisir SUCCES ou ECHEC"},
                status=status.HTTP_400_BAD_REQUEST
            )

        deploiement.statut = nouveau_statut
        deploiement.save()

        niveau = Journal.Niveau.INFO if nouveau_statut == 'SUCCES' else Journal.Niveau.ERROR
        message = (
            f"Déploiement #{deploiement.id} terminé avec succès"
            if nouveau_statut == 'SUCCES'
            else f"Déploiement #{deploiement.id} échoué"
        )
        Journal.objects.create(
            deploiement=deploiement,
            niveau=niveau,
            message=message,
            source='system'
        )

        return Response({
            'message': message,
            'statut': deploiement.statut,
        })

    @action(detail=True, methods=['get'])
    def journaux(self, request, pk=None):
        """Récupère tous les journaux d'un déploiement"""
        deploiement = self.get_object()
        journaux = Journal.objects.filter(
            deploiement=deploiement
        ).order_by('horodatage')

        niveau = request.query_params.get('niveau')
        if niveau:
            journaux = journaux.filter(niveau=niveau)

        serializer = JournalSerializer(journaux, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def ajouter_journal(self, request, pk=None):
        """Ajoute un journal à un déploiement"""
        deploiement = self.get_object()
        serializer = JournalSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(deploiement=deploiement)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)