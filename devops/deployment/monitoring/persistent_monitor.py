"""Persistent deployment monitor — DB-backed equivalent of DeploymentMonitor."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from devops.deployment.events.event_bus import EventBus
from devops.deployment.progress.stage_tracker import StageTracker
from devops.models import DeploymentJob, DeploymentLogEntry, DeploymentStageProgress, DeploymentEvent

logger = logging.getLogger(__name__)


class PersistentDeploymentMonitor:
    """Drop-in replacement for DeploymentMonitor backed by the database.

    Maintains the same duck-type interface: track(), update_phase(), get_status(), list_deployments().
    Additionally persists log entries, events, and stage progress.
    """

    def __init__(self, event_bus: Optional[EventBus] = None):
        self._event_bus = event_bus or EventBus()

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    def track(self, deployment_id: str, result: Any = None) -> None:
        """Register a deployment for monitoring."""
        job, _ = DeploymentJob.objects.get_or_create(
            deployment_id=deployment_id,
            defaults={
                'status': DeploymentJob.Status.RUNNING,
                'started_at': timezone.now(),
                'provider_name': 'unknown',
                'project_data': {},
                'artifacts_data': {},
            },
        )
        self._event_bus.publish('deployment.started', {'deployment_id': deployment_id})
        logger.info('PersistentMonitor: now tracking deployment %s', deployment_id)

    def _get_job(self, deployment_id: str):
        """Fetch a DeploymentJob, returning None for invalid IDs."""
        try:
            return DeploymentJob.objects.get(deployment_id=deployment_id)
        except (DeploymentJob.DoesNotExist, ValueError, DjangoValidationError, TypeError):
            return None

    def update_phase(self, deployment_id: str, phase: str) -> None:
        """Record a phase transition for the given deployment."""
        job = self._get_job(deployment_id)
        if job is None:
            logger.warning('PersistentMonitor: unknown deployment %s', deployment_id)
            return

        stage_name = StageTracker.map_phase_to_stage(phase)
        if stage_name:
            sp, _ = DeploymentStageProgress.objects.get_or_create(
                job=job,
                stage_name=stage_name,
                defaults={
                    'order': next(
                        (s['order'] for s in StageTracker.get_all_stages() if s['name'] == stage_name),
                        0,
                    ),
                },
            )
            if phase not in ('initializing',):
                sp.status = 'RUNNING'
                sp.started_at = sp.started_at or timezone.now()
                sp.save()

        job.current_stage = stage_name or phase
        completed_stages = list(
            DeploymentStageProgress.objects.filter(job=job, status='COMPLETED').values_list('stage_name', flat=True)
        )
        job.progress_percent = StageTracker.calculate_progress(completed_stages)
        job.save()

        self._event_bus.publish('deployment.phase_changed', {
            'deployment_id': deployment_id,
            'phase': phase,
        })
        logger.info('PersistentMonitor: %s -> %s', deployment_id, phase)

    def mark_stage_completed(self, deployment_id: str, stage_name: str) -> None:
        """Mark a specific stage as completed."""
        job = self._get_job(deployment_id)
        if job is None:
            return

        sp, _ = DeploymentStageProgress.objects.get_or_create(
            job=job,
            stage_name=stage_name,
            defaults={
                'order': next(
                    (s['order'] for s in StageTracker.get_all_stages() if s['name'] == stage_name),
                    0,
                ),
            },
        )
        sp.status = 'COMPLETED'
        sp.finished_at = timezone.now()
        sp.save()

        completed_stages = list(
            DeploymentStageProgress.objects.filter(job=job, status='COMPLETED').values_list('stage_name', flat=True)
        )
        job.progress_percent = StageTracker.calculate_progress(completed_stages)
        job.save()

    def mark_completed(self, deployment_id: str) -> None:
        """Mark a deployment as completed successfully."""
        job = self._get_job(deployment_id)
        if job is None:
            return
        job.status = DeploymentJob.Status.COMPLETED
        job.finished_at = timezone.now()
        job.progress_percent = 100
        job.save()
        self._event_bus.publish('deployment.completed', {'deployment_id': deployment_id})

    def mark_failed(self, deployment_id: str, error: str = '') -> None:
        """Mark a deployment as failed."""
        job = self._get_job(deployment_id)
        if job is None:
            return
        job.status = DeploymentJob.Status.FAILED
        job.finished_at = timezone.now()
        job.error_message = error
        job.save()
        self._event_bus.publish('deployment.failed', {'deployment_id': deployment_id, 'error': error})

    def mark_cancelled(self, deployment_id: str) -> None:
        """Mark a deployment as cancelled."""
        job = self._get_job(deployment_id)
        if job is None:
            return
        job.status = DeploymentJob.Status.CANCELLED
        job.finished_at = timezone.now()
        job.save()
        self._event_bus.publish('deployment.cancelled', {'deployment_id': deployment_id})

    def add_log(self, deployment_id: str, message: str, level: str = 'INFO', stage: str = '') -> None:
        """Persist a log entry for the deployment."""
        job = self._get_job(deployment_id)
        if job is None:
            return
        DeploymentLogEntry.objects.create(
            job=job,
            level=level,
            message=message,
            stage=stage,
        )

    def add_event(self, deployment_id: str, event_type: str, payload: Optional[dict] = None) -> None:
        """Persist an event and publish to the event bus."""
        job = self._get_job(deployment_id)
        if job is None:
            return
        DeploymentEvent.objects.create(
            job=job,
            event_type=event_type,
            payload=payload or {},
        )

    def get_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Return the current phase and history of a deployment."""
        job = self._get_job(deployment_id)
        if job is None:
            return None

        stages = list(
            DeploymentStageProgress.objects.filter(job=job).order_by('order').values(
                'stage_name', 'status', 'progress_percent', 'started_at', 'finished_at'
            )
        )

        return {
            'deployment_id': str(job.deployment_id),
            'phase': job.current_stage,
            'status': job.status,
            'progress_percent': job.progress_percent,
            'stages': stages,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'finished_at': job.finished_at.isoformat() if job.finished_at else None,
            'error_message': job.error_message,
        }

    def list_deployments(self) -> Dict[str, str]:
        """Return a mapping of deployment_id -> current phase."""
        jobs = DeploymentJob.objects.all()
        return {str(j.deployment_id): j.status for j in jobs}
