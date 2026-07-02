from rest_framework import viewsets, permissions
from .models import ProjetApplicatif
from .serializers import ProjetApplicatifSerializer


class ProjetApplicatifViewSet(viewsets.ModelViewSet):
    serializer_class = ProjetApplicatifSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Chaque utilisateur ne voit que ses propres projets
        return ProjetApplicatif.objects.filter(proprietaire=self.request.user)

    def perform_create(self, serializer):
        serializer.save(proprietaire=self.request.user)
