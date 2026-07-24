"""CI/CD pipeline generator interface."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping

from .artifact_generator import ArtifactGenerator


class PipelineGeneratorInterface(ArtifactGenerator):
    """Contract for CI/CD pipeline artifact generation."""

    artifact_type = 'pipeline'

    @abstractmethod
    def generate_pipeline(self, project: Mapping[str, Any]) -> str:
        """Generate a CI/CD pipeline descriptor."""
        raise NotImplementedError
