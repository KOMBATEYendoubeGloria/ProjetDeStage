"""View for project analysis endpoint."""

from __future__ import annotations

import logging

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from devops.api.responses.standard import StandardResponse
from devops.api.serializers.project_analysis import ProjectAnalysisSerializer
from devops.generators.analyzer.project_analyzer import ProjectAnalyzer

logger = logging.getLogger(__name__)


class AnalyzeView(APIView):
    """POST /api/devops/analyze/

    Analyzes a project definition and returns enriched metadata.

    The view delegates entirely to ``ProjectAnalyzer``.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request):
        serializer = ProjectAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(
                errors=list(serializer.errors.values()),
                message='Validation failed',
                status_code=400,
            )

        data = serializer.validated_data

        try:
            analyzer = ProjectAnalyzer()
            if data.get('path'):
                result = analyzer.analyze(data['path'])
            else:
                result = analyzer.analyze(data)
        except Exception as exc:
            logger.exception('Project analysis failed')
            return StandardResponse.error(
                errors=[str(exc)],
                message='Project analysis failed',
                status_code=500,
            )

        return StandardResponse.success(data=result, message='Project analyzed successfully')
