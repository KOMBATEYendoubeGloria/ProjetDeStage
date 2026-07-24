"""Environment generator interface."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping

from .artifact_generator import ArtifactGenerator


class EnvironmentGeneratorInterface(ArtifactGenerator):
    """Contract for environment artifact generation."""

    artifact_type = 'environment'

    @abstractmethod
    def generate_environment(self, project: Mapping[str, Any]) -> str:
        """Generate environment file content."""
        raise NotImplementedError
