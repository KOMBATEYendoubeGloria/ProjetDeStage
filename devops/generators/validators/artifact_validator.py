"""Validation helpers for generated DevOps artifacts."""

from __future__ import annotations

import logging
from typing import Any, Mapping

logger = logging.getLogger(__name__)


class ArtifactValidator:
    """Validate generation input and surface explicit errors."""

    REQUIRED_FIELDS = {
        'name': 'Project name is required',
        'type': 'Application type is required',
        'framework': 'Application framework is required',
        'language': 'Language is required',
        'version': 'Version is required',
    }

    def validate(self, project: Mapping[str, Any]) -> None:
        for field, message in self.REQUIRED_FIELDS.items():
            if not project.get(field):
                logger.error('Artifact validation failed: %s', message)
                raise ValueError(message)

        if not isinstance(project.get('ports', []), list):
            logger.error('Artifact validation failed: ports must be provided as a list')
            raise ValueError('ports must be provided as a list')
