"""Deployment job manager — async execution engine."""

from __future__ import annotations

import logging
import threading
import uuid
from typing import Any, Dict, Optional

from devops.deployment.orchestrator.deployment_orchestrator import DeploymentOrchestrator
from devops.models import DeploymentJob
from devops.deployment.async_engine.backends import JobBackend, ThreadJobBackend
from devops.deployment.async_engine.cancellation import CancellationToken, CancellationError
from devops.deployment.events.event_bus import EventBus
from devops.deployment.monitoring.persistent_monitor import PersistentDeploymentMonitor
from devops.deployment.progress.stage_tracker import STAGES

logger = logging.getLogger(__name__)


class DeploymentJobManager:
    """Manages async deployment jobs via a pluggable JobBackend.

    Orchestrates: backend.submit → DeploymentOrchestrator.deploy → persistent_monitor.
    Supports cancellation at stage boundaries via CancellationToken.
    """

    def __init__(
        self,
        backend: Optional[JobBackend] = None,
        event_bus: Optional[EventBus] = None,
        monitor: Optional[PersistentDeploymentMonitor] = None,
    ):
        self._backend = backend or ThreadJobBackend()
        self._event_bus = event_bus or EventBus()
        self._monitor = monitor or PersistentDeploymentMonitor(event_bus=self._event_bus)
        self._tokens: Dict[str, CancellationToken] = {}
        self._lock = threading.Lock()

    @property
    def backend(self) -> JobBackend:
        return self._backend

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    @property
    def monitor(self) -> PersistentDeploymentMonitor:
        return self._monitor

    def submit(
        self,
        provider_name: str,
        project: Dict[str, Any],
        artifacts: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Submit a new deployment job. Returns the deployment_id (UUID)."""
        deployment_id = str(uuid.uuid4())

        job_record = DeploymentJob.objects.create(
            deployment_id=deployment_id,
            provider_name=provider_name,
            project_data=project,
            artifacts_data=artifacts,
            config_data=config or {},
            status=DeploymentJob.Status.QUEUED,
        )

        token = CancellationToken()
        with self._lock:
            self._tokens[deployment_id] = token

        orchestrator = DeploymentOrchestrator(monitoring=self._monitor)

        self._monitor.track(deployment_id)
        self._monitor.add_log(deployment_id, 'Job submitted and queued')
        self._event_bus.publish('deployment.queued', {'deployment_id': deployment_id})

        def _execute():
            try:
                job_record.status = DeploymentJob.Status.RUNNING
                job_record.started_at = __import__('django.utils.timezone', fromlist=['now']).now()
                job_record.save()

                self._event_bus.publish('deployment.started', {'deployment_id': deployment_id})

                for stage_name, weight in STAGES:
                    token.throw_if_cancelled()

                    self._monitor.update_phase(deployment_id, stage_name.lower())
                    self._monitor.add_log(deployment_id, f'Starting stage: {stage_name}')

                    if stage_name == 'VALIDATION':
                        orchestrator._validate(project, artifacts, config or {})
                        self._monitor.mark_stage_completed(deployment_id, stage_name)

                    elif stage_name == 'COMPLETED':
                        self._monitor.mark_stage_completed(deployment_id, stage_name)

                result = orchestrator.deploy(
                    provider_name=provider_name,
                    project=project,
                    artifacts=artifacts,
                    config=config or {},
                )

                job_record.refresh_from_db()
                if result.status == 'SUCCESS':
                    job_record.status = DeploymentJob.Status.COMPLETED
                    job_record.progress_percent = 100
                    self._monitor.mark_completed(deployment_id)
                else:
                    job_record.status = DeploymentJob.Status.FAILED
                    job_record.error_message = '; '.join(result.errors) if result.errors else 'Deployment failed'
                    self._monitor.mark_failed(deployment_id, job_record.error_message)

                from django.utils import timezone as tz
                job_record.finished_at = tz.now()
                job_record.save()

                self._event_bus.publish('deployment.finished', {
                    'deployment_id': deployment_id,
                    'status': job_record.status,
                })

            except CancellationError:
                job_record.refresh_from_db()
                job_record.status = DeploymentJob.Status.CANCELLED
                from django.utils import timezone as tz
                job_record.finished_at = tz.now()
                job_record.save()
                self._monitor.mark_cancelled(deployment_id)
                self._event_bus.publish('deployment.cancelled', {'deployment_id': deployment_id})

            except Exception as exc:
                logger.exception('Deployment job %s failed unexpectedly', deployment_id)
                job_record.refresh_from_db()
                job_record.status = DeploymentJob.Status.FAILED
                job_record.error_message = str(exc)
                from django.utils import timezone as tz
                job_record.finished_at = tz.now()
                job_record.save()
                self._monitor.mark_failed(deployment_id, str(exc))
                self._event_bus.publish('deployment.error', {'deployment_id': deployment_id, 'error': str(exc)})

        self._backend.submit(deployment_id, _execute)
        logger.info('DeploymentJobManager: submitted job %s', deployment_id)
        return deployment_id

    def cancel(self, deployment_id: str) -> None:
        """Request cancellation of a running deployment job."""
        with self._lock:
            token = self._tokens.get(deployment_id)
        if token:
            token.cancel()
            self._backend.cancel(deployment_id)
            self._monitor.add_log(deployment_id, 'Cancellation requested by user', level='WARNING')
            self._event_bus.publish('deployment.cancel_requested', {'deployment_id': deployment_id})
            logger.info('DeploymentJobManager: cancellation requested for %s', deployment_id)

    def get_status(self, deployment_id: str) -> Optional[dict]:
        """Return the full deployment status from the monitor."""
        return self._monitor.get_status(deployment_id)

    def list_jobs(self) -> Dict[str, str]:
        """Return deployment_id -> status for all tracked jobs."""
        return self._monitor.list_deployments()
