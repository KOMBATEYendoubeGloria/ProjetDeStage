"""Docker-focused generator interface."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping

from .artifact_generator import ArtifactGenerator


class DockerGeneratorInterface(ArtifactGenerator):
    """Contract for Docker and compose artifact generation."""

    artifact_type = 'docker'

    @abstractmethod
    def generate_dockerfile(self, project: Mapping[str, Any]) -> str:
        """Create a Dockerfile for the project."""
        raise NotImplementedError

    @abstractmethod
    def generate_docker_compose(self, project: Mapping[str, Any]) -> str:
        """Create a docker-compose definition."""
        raise NotImplementedError
