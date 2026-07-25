"""Deployment monitor — tracks deployment phases and progress."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..result import DeploymentResult

logger = logging.getLogger(__name__)


class DeploymentMonitor:
    """Tracks the lifecycle of deployments via phase transitions.

    Stores in-memory state keyed by deployment_id. Designed to be
    extended with database-backed persistence in future phases.
    """

    def __init__(self):
        self._deployments: Dict[str, Dict[str, Any]] = {}

    def track(self, deployment_id: str, result: DeploymentResult) -> None:
        """Register a deployment for monitoring."""
        self._deployments[deployment_id] = {
            'result': result,
            'phase': 'initializing',
            'history': ['initializing'],
        }
        logger.info('Now tracking deployment: %s', deployment_id)

    def update_phase(self, deployment_id: str, phase: str) -> None:
        """Record a phase transition for the given deployment."""
        entry = self._deployments.get(deployment_id)
        if entry is None:
            logger.warning('Unknown deployment id: %s', deployment_id)
            return
        entry['phase'] = phase
        entry['history'].append(phase)
        logger.info('Deployment %s -> phase: %s', deployment_id, phase)

    def get_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Return the current phase and history of a deployment."""
        entry = self._deployments.get(deployment_id)
        if entry is None:
            return None
        return {
            'deployment_id': deployment_id,
            'phase': entry['phase'],
            'history': list(entry['history']),
        }

    def list_deployments(self) -> Dict[str, str]:
        """Return a mapping of deployment_id → current phase."""
        return {
            did: entry['phase']
            for did, entry in self._deployments.items()
        }
