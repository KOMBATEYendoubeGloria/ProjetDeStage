"""Default Docker artifact generator implementation."""

from __future__ import annotations

import logging
from typing import Any, Mapping

from ...interfaces.docker_generator import DockerGeneratorInterface
from ...validators.artifact_validator import ArtifactValidator

logger = logging.getLogger(__name__)


class DefaultDockerGenerator(DockerGeneratorInterface):
    """Generate Dockerfile and docker-compose content from a project definition."""

    artifact_type = 'docker'

    def __init__(self) -> None:
        self.validator = ArtifactValidator()

    def generate(self, project: Mapping[str, Any]) -> str:
        return self.generate_dockerfile(project)

    def generate_dockerfile(self, project: Mapping[str, Any]) -> str:
        self.validator.validate(project)
        logger.info('Generating Dockerfile for %s', project['name'])
        app_type = project.get('type', 'generic')
        port = project.get('ports', [8000])[0]
        return (
            f"FROM python:{project.get('version', '3.11')}-slim\n"
            "WORKDIR /app\n"
            "RUN adduser --system --group appuser\n"
            "COPY . .\n"
            f"EXPOSE {port}\n"
            "USER appuser\n"
            f"CMD [\"python\", \"manage.py\", \"runserver\", \"0.0.0.0:{port}\"]\n"
        )

    def generate_docker_compose(self, project: Mapping[str, Any]) -> str:
        self.validator.validate(project)
        logger.info('Generating docker-compose for %s', project['name'])
        port = project.get('ports', [8000])[0]
        image = project.get('docker_image', f"{project['name']}:latest")
        return (
            "version: '3.9'\n"
            "services:\n"
            f"  {project['name']}:\n"
            f"    image: {image}\n"
            f"    ports:\n"
            f"      - \"{port}:{port}\"\n"
            "    environment:\n"
            "      ENVIRONMENT: dev\n"
        )
