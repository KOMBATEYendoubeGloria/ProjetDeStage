"""Ansible generator interface."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping

from .artifact_generator import ArtifactGenerator


class AnsibleGeneratorInterface(ArtifactGenerator):
    """Contract for Ansible artifact generation."""

    artifact_type = 'ansible'

    @abstractmethod
    def generate_ansible(self, project: Mapping[str, Any]) -> str:
        """Create the Ansible playbook and inventory content."""
        raise NotImplementedError
