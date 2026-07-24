"""Views for individual artifact generation endpoints."""

from __future__ import annotations

import logging

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from devops.api.responses.standard import StandardResponse
from devops.api.serializers.artifact_generation import ArtifactGenerationSerializer
from devops.generators.engine.artifact_engine import ArtifactEngine

logger = logging.getLogger(__name__)


class _BaseArtifactView(APIView):
    """Base class for individual artifact generation views.

    Subclasses set ``_generate_method`` to the engine method name.
    """

    permission_classes = [AllowAny]
    _generate_method: str = ''

    def post(self, request: Request):
        serializer = ArtifactGenerationSerializer(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(
                errors=list(serializer.errors.values()),
                message='Validation failed',
                status_code=400,
            )

        project = serializer.validated_data

        try:
            engine = ArtifactEngine()
            generator = getattr(engine, self._generate_method)
            content = generator(project)
        except Exception as exc:
            logger.exception('%s generation failed', self._generate_method)
            return StandardResponse.error(
                errors=[str(exc)],
                message=f'{self._generate_method} failed',
                status_code=500,
            )

        return StandardResponse.success(
            data={self._generate_method: content},
            message=f'{self._generate_method} generated successfully',
        )


class DockerfileView(_BaseArtifactView):
    """POST /api/devops/artifacts/docker/"""
    _generate_method = 'generate_dockerfile'


class DockerComposeView(_BaseArtifactView):
    """POST /api/devops/artifacts/docker-compose/"""
    _generate_method = 'generate_docker_compose'


class EnvironmentView(_BaseArtifactView):
    """POST /api/devops/artifacts/environment/"""
    _generate_method = 'generate_environment'


class TerraformView(_BaseArtifactView):
    """POST /api/devops/artifacts/terraform/"""
    _generate_method = 'generate_terraform'


class AnsibleView(_BaseArtifactView):
    """POST /api/devops/artifacts/ansible/"""
    _generate_method = 'generate_ansible'


class PipelineView(_BaseArtifactView):
    """POST /api/devops/artifacts/pipeline/"""
    _generate_method = 'generate_pipeline'


class AllArtifactsView(APIView):
    """POST /api/devops/artifacts/all/

    Generates all DevOps artifacts and returns a ``GeneratedArtifacts`` object.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request):
        serializer = ArtifactGenerationSerializer(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(
                errors=list(serializer.errors.values()),
                message='Validation failed',
                status_code=400,
            )

        project = serializer.validated_data

        try:
            engine = ArtifactEngine()
            artifacts = engine.generate_all(project)
        except Exception as exc:
            logger.exception('Artifact generation failed')
            return StandardResponse.error(
                errors=[str(exc)],
                message='Artifact generation failed',
                status_code=500,
            )

        return StandardResponse.success(
            data=artifacts.to_dict(),
            message='All artifacts generated successfully',
        )
