"""Health check endpoint for the DevOps API."""

from __future__ import annotations

from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from devops.api.responses.standard import StandardResponse


class HealthCheckView(APIView):
    """GET /api/devops/health/

    Returns API and database health status.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request):
        db_ok = True
        try:
            connection.ensure_connection()
        except Exception:
            db_ok = False

        status_data = {
            'api': 'healthy',
            'database': 'healthy' if db_ok else 'unhealthy',
        }

        all_healthy = all(v == 'healthy' for v in status_data.values())
        status_code = 200 if all_healthy else 503

        return StandardResponse.success(
            data=status_data,
            message='Health check passed' if all_healthy else 'Health check degraded',
            status_code=status_code,
        )
