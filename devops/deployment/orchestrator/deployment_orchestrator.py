"""Deployment orchestrator — coordinates providers, executors, and monitoring."""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from ..exceptions import DeploymentEngineError, DeploymentValidationError, RollbackError
from ..providers.base import ProviderRegistry
from ..result import DeploymentResult

logger = logging.getLogger(__name__)


class DeploymentOrchestrator:
    """High-level orchestrator that drives a full deployment lifecycle.

    Lifecycle: validate → provision → deploy → verify.
    On failure: rollback (teardown) and record errors.
    """

    def __init__(self, monitoring=None):
        from ..monitoring.deployment_monitor import DeploymentMonitor
        self.monitoring = monitoring or DeploymentMonitor()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def deploy(
        self,
        provider_name: str,
        project: Dict[str, Any],
        artifacts: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> DeploymentResult:
        """Execute the full deployment lifecycle for the given provider."""
        deployment_id = str(uuid.uuid4())
        result = DeploymentResult(provider=provider_name, deployment_id=deployment_id)

        result.add_log(f'Starting deployment {deployment_id}')
        result.mark_started()
        self.monitoring.track(deployment_id, result)

        try:
            self._validate(project, artifacts)
            provider = self._get_provider(provider_name, config)

            result.add_log('Provisioning infrastructure')
            self.monitoring.update_phase(deployment_id, 'provisioning')
            provision_output = provider.provision(project, artifacts, config)
            result.outputs['provision'] = provision_output

            result.add_log('Deploying application')
            self.monitoring.update_phase(deployment_id, 'deploying')
            deploy_output = provider.deploy(project, artifacts, config)
            result.outputs['deploy'] = deploy_output

            result.add_log('Deployment completed successfully')
            result.mark_completed()
            self.monitoring.update_phase(deployment_id, 'completed')

        except DeploymentValidationError:
            result.mark_failed('Validation error')
            self.monitoring.update_phase(deployment_id, 'failed')
        except DeploymentEngineError as exc:
            logger.error('Deployment failed: %s', exc)
            result.mark_failed(str(exc))
            self.monitoring.update_phase(deployment_id, 'failed')
            try:
                self._rollback(provider_name, project, config, result)
            except RollbackError:
                pass
        except Exception as exc:
            logger.exception('Unexpected deployment error')
            result.mark_failed(f'Unexpected error: {exc}')
            self.monitoring.update_phase(deployment_id, 'failed')
            try:
                self._rollback(provider_name, project, config, result)
            except RollbackError:
                pass

        result.add_log(f'Deployment finished with status: {result.status}')
        return result

    def teardown(
        self,
        provider_name: str,
        project: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> DeploymentResult:
        """Destroy infrastructure for the given provider."""
        deployment_id = str(uuid.uuid4())
        result = DeploymentResult(provider=provider_name, deployment_id=deployment_id)
        result.mark_started()
        result.add_log(f'Tearing down {provider_name}')

        try:
            provider = self._get_provider(provider_name, config)
            provider.teardown(project, config)
            result.mark_completed()
            result.add_log('Teardown completed')
        except Exception as exc:
            result.mark_failed(str(exc))
            result.add_log(f'Teardown failed: {exc}')

        return result

    def status(
        self,
        provider_name: str,
        project: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Return the current status for a provider deployment."""
        provider = self._get_provider(provider_name, config)
        return provider.status(project, config)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate(self, project: Dict[str, Any], artifacts: Dict[str, Any]) -> None:
        """Validate deployment inputs before execution."""
        if not project:
            raise DeploymentValidationError('Project data is required')
        if not artifacts:
            raise DeploymentValidationError('Artifacts are required')
        project_name = project.get('name', '')
        if not project_name:
            raise DeploymentValidationError('Project name is required')

    def _get_provider(self, provider_name: str, config: Optional[Dict[str, Any]] = None):
        """Look up and instantiate the provider from the registry."""
        try:
            return ProviderRegistry.create(provider_name, config=config)
        except ValueError as exc:
            raise DeploymentEngineError(f'Provider not found: {provider_name}') from exc

    def _rollback(
        self,
        provider_name: str,
        project: Dict[str, Any],
        config: Optional[Dict[str, Any]],
        result: DeploymentResult,
    ) -> None:
        """Attempt to tear down resources after a failed deployment."""
        result.add_log('Initiating rollback')
        try:
            provider = self._get_provider(provider_name, config)
            provider.teardown(project, config)
            result.add_log('Rollback completed')
        except Exception as exc:
            result.add_log(f'Rollback failed: {exc}')
            raise RollbackError(f'Rollback failed: {exc}') from exc
