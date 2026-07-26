"""Views for asynchronous deployment monitoring."""

from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from devops.api.responses.standard import StandardResponse
from devops.api.serializers.async_deployment import (
    AsyncDeploymentStartSerializer,
    DeploymentStatusSerializer,
)
from devops.deployment.async_engine.job_manager import DeploymentJobManager
from devops.deployment.events.event_bus import EventBus
from devops.deployment.monitoring.persistent_monitor import PersistentDeploymentMonitor
from devops.models import DeploymentJob, DeploymentLogEntry, DeploymentEvent

logger = logging.getLogger(__name__)


def _get_job_manager() -> DeploymentJobManager:
    """Create a fresh DeploymentJobManager for each request.

    This is a simple approach; in production you'd use dependency injection.
    """
    event_bus = EventBus()
    monitor = PersistentDeploymentMonitor(event_bus=event_bus)
    return DeploymentJobManager(event_bus=event_bus, monitor=monitor)


class AsyncDeploymentStartView(APIView):
    """POST /api/deployment/async/start — submit a new async deployment job."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = AsyncDeploymentStartSerializer(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(
                errors=list(serializer.errors.keys()),
                message='Validation error',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        manager = _get_job_manager()

        try:
            deployment_id = manager.submit(
                provider_name=data['provider_name'],
                project=data['project'],
                artifacts=data['artifacts'],
                config=data.get('config', {}),
            )
            return StandardResponse.success({
                'deployment_id': deployment_id,
                'message': 'Deployment job submitted',
            }, status_code=status.HTTP_201_CREATED)
        except Exception as exc:
            logger.exception('Failed to submit deployment job')
            return StandardResponse.error(
                errors=[str(exc)],
                message='Failed to submit deployment',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AsyncDeploymentStatusView(APIView):
    """GET /api/deployment/async/<deployment_id>/status — get deployment status."""

    permission_classes = [AllowAny]

    def get(self, request: Request, deployment_id: str) -> Response:
        monitor = PersistentDeploymentMonitor()
        status_data = monitor.get_status(deployment_id)
        if status_data is None:
            return StandardResponse.error(
                errors=['Deployment not found'],
                message='Deployment not found',
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return StandardResponse.success(status_data)


class AsyncDeploymentCancelView(APIView):
    """POST /api/deployment/async/<deployment_id>/cancel — cancel a deployment."""

    permission_classes = [AllowAny]

    def post(self, request: Request, deployment_id: str) -> Response:
        manager = _get_job_manager()
        manager.cancel(deployment_id)
        return StandardResponse.success({'deployment_id': deployment_id, 'message': 'Cancellation requested'})


class AsyncDeploymentLogsView(APIView):
    """GET /api/deployment/async/<deployment_id>/logs — get deployment logs."""

    permission_classes = [AllowAny]

    def get(self, request: Request, deployment_id: str) -> Response:
        try:
            job = DeploymentJob.objects.get(deployment_id=deployment_id)
        except DeploymentJob.DoesNotExist:
            return StandardResponse.error(
                errors=['Deployment not found'],
                message='Deployment not found',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        logs = DeploymentLogEntry.objects.filter(job=job).order_by('timestamp')
        logs_data = [
            {
                'timestamp': log.timestamp.isoformat(),
                'level': log.level,
                'message': log.message,
                'stage': log.stage,
            }
            for log in logs
        ]
        return StandardResponse.success({'deployment_id': deployment_id, 'logs': logs_data})


class AsyncDeploymentEventsView(APIView):
    """GET /api/deployment/async/<deployment_id>/events — get deployment events."""

    permission_classes = [AllowAny]

    def get(self, request: Request, deployment_id: str) -> Response:
        try:
            job = DeploymentJob.objects.get(deployment_id=deployment_id)
        except DeploymentJob.DoesNotExist:
            return StandardResponse.error(
                errors=['Deployment not found'],
                message='Deployment not found',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        events = DeploymentEvent.objects.filter(job=job).order_by('created_at')
        events_data = [
            {
                'event_type': event.event_type,
                'payload': event.payload,
                'created_at': event.created_at.isoformat(),
            }
            for event in events
        ]
        return StandardResponse.success({'deployment_id': deployment_id, 'events': events_data})


class AsyncDeploymentListView(APIView):
    """GET /api/deployment/async/list — list all deployment jobs."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        jobs = DeploymentJob.objects.all()[:50]
        jobs_data = [
            {
                'deployment_id': str(job.deployment_id),
                'provider_name': job.provider_name,
                'status': job.status,
                'current_stage': job.current_stage,
                'progress_percent': job.progress_percent,
                'created_at': job.created_at.isoformat(),
                'finished_at': job.finished_at.isoformat() if job.finished_at else None,
            }
            for job in jobs
        ]
        return StandardResponse.success({'jobs': jobs_data})
