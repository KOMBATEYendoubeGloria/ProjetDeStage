"""Terraform generator interface."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping

from .artifact_generator import ArtifactGenerator


class TerraformGeneratorInterface(ArtifactGenerator):
    """Contract for Terraform artifact generation."""

    artifact_type = 'terraform'

    @abstractmethod
    def generate_terraform(self, project: Mapping[str, Any]) -> str:
        """Create Terraform manifest content."""
        raise NotImplementedError
