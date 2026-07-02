from rest_framework import viewsets, permissions
from .models import Deploiement
from .serializers import DeploiementSerializer


class DeploiementViewSet(viewsets.ModelViewSet):
    serializer_class = DeploiementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Deploiement.objects.filter(projet__proprietaire=self.request.user)
