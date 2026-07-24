from rest_framework import views
from rest_framework.response import Response


class DevopsHealthCheckView(views.APIView):
    """Minimal placeholder view for devops application structure."""
    permission_classes = []

    def get(self, request):
        return Response({'status': 'devops app placeholder'})
