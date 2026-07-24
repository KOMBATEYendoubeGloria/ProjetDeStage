"""Views for generation history endpoints."""

from __future__ import annotations

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from devops.api.responses.standard import StandardResponse
from devops.api.serializers.generation_history import GenerationHistorySerializer
from devops.models import GenerationHistory


class GenerationHistoryListView(APIView):
    """GET /api/devops/history/

    Lists all generation history records ordered by most recent.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request):
        qs = GenerationHistory.objects.all()
        serializer = GenerationHistorySerializer(qs, many=True)
        return StandardResponse.success(
            data=serializer.data,
            message='Generation history retrieved',
        )


class GenerationHistoryDetailView(APIView):
    """GET /api/devops/history/<id>/

    Retrieves a single generation history record.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, pk: int):
        try:
            record = GenerationHistory.objects.get(pk=pk)
        except GenerationHistory.DoesNotExist:
            return StandardResponse.error(
                errors=[f'Generation history record {pk} not found'],
                message='Record not found',
                status_code=404,
            )

        serializer = GenerationHistorySerializer(record)
        return StandardResponse.success(
            data=serializer.data,
            message='Generation history record retrieved',
        )
