"""Deployment services — high-level service layer for the REST API."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..exceptions import DeploymentEngineError
from ..orchestrator.deployment_orchestrator import DeploymentOrchestrator
from ..providers.base import ProviderRegistry
from ..result import DeploymentResult

logger = logging.getLogger(__name__)


class DeploymentService:
    """Facade used by the REST API to trigger deployments via the orchestrator."""

    def __init__(self, orchestrator: Optional[DeploymentOrchestrator] = None):
        self.orchestrator = orchestrator or DeploymentOrchestrator()

    def start_deployment(
        self,
        provider_name: str,
        project: Dict[str, Any],
        artifacts: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> DeploymentResult:
        """Start a new deployment through the orchestrator."""
        logger.info('DeploymentService: starting deployment via %s', provider_name)
        return self.orchestrator.deploy(provider_name, project, artifacts, config)

    def teardown(
        self,
        provider_name: str,
        project: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> DeploymentResult:
        """Tear down an existing deployment."""
        logger.info('DeploymentService: tearing down %s', provider_name)
        return self.orchestrator.teardown(provider_name, project, config)

    def status(
        self,
        provider_name: str,
        project: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Return the current deployment status."""
        return self.orchestrator.status(provider_name, project, config)

    @staticmethod
    def available_providers():
        """Return the list of registered provider names."""
        return ProviderRegistry.available()
