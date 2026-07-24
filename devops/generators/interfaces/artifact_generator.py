"""Base interface for DevOps artifact generators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping


class ArtifactGenerator(ABC):
    """Common contract for all artifact generators."""

    artifact_type: str = 'generic'

    @abstractmethod
    def generate(self, project: Mapping[str, Any]) -> str:
        """Generate a single artifact from a project definition."""
        raise NotImplementedError
