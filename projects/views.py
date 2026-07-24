from rest_framework import viewsets, permissions, filters
from .models import ProjetApplicatif
from .serializers import ProjetApplicatifSerializer


class ProjetApplicatifViewSet(viewsets.ModelViewSet):
    serializer_class = ProjetApplicatifSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'technologie', 'branche']
    ordering_fields = ['date_creation', 'nom']
    ordering = ['-date_creation']

    def get_queryset(self):
        return ProjetApplicatif.objects.filter(
            proprietaire=self.request.user
        ).select_related('proprietaire')

    def perform_create(self, serializer):
        serializer.save(proprietaire=self.request.user)