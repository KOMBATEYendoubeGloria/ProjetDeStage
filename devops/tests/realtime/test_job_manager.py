"""Tests for DeploymentJobManager."""

import uuid

from django.test import TestCase, override_settings

from devops.deployment.async_engine.backends.thread import ThreadJobBackend
from devops.deployment.async_engine.job_manager import DeploymentJobManager
from devops.deployment.events.event_bus import EventBus
from devops.deployment.monitoring.persistent_monitor import PersistentDeploymentMonitor
from devops.models import DeploymentJob


@override_settings(SECURE_SSL_REDIRECT=False)
class DeploymentJobManagerTests(TestCase):
    """Tests for DeploymentJobManager.

    Note: Background thread DB operations are tested via PersistentDeploymentMonitor tests.
    These tests focus on the synchronous coordination layer.
    """

    def setUp(self):
        self.backend = ThreadJobBackend(max_workers=2)
        self.event_bus = EventBus()
        self.monitor = PersistentDeploymentMonitor(event_bus=self.event_bus)
        self.manager = DeploymentJobManager(
            backend=self.backend,
            event_bus=self.event_bus,
            monitor=self.monitor,
        )

    def tearDown(self):
        self.backend.shutdown(wait=False)

    def test_submit_creates_job_record(self):
        deployment_id = self.manager.submit(
            provider_name='docker',
            project={'name': 'test-app', 'type': 'web'},
            artifacts={'dockerfile': 'FROM python:3.11'},
        )
        self.assertIsNotNone(deployment_id)
        job = DeploymentJob.objects.get(deployment_id=deployment_id)
        self.assertEqual(job.provider_name, 'docker')
        self.assertEqual(job.status, DeploymentJob.Status.QUEUED)

    def test_submit_returns_uuid(self):
        deployment_id = self.manager.submit(
            provider_name='docker',
            project={'name': 'test', 'type': 'web'},
            artifacts={},
        )
        uuid.UUID(deployment_id)

    def test_submit_stores_project_data(self):
        project = {'name': 'my-app', 'type': 'api'}
        artifacts = {'dockerfile': 'FROM alpine'}
        deployment_id = self.manager.submit(
            provider_name='docker',
            project=project,
            artifacts=artifacts,
        )
        job = DeploymentJob.objects.get(deployment_id=deployment_id)
        self.assertEqual(job.project_data, project)
        self.assertEqual(job.artifacts_data, artifacts)

    def test_submit_stores_config(self):
        config = {'remote': True, 'host': '10.0.0.1'}
        deployment_id = self.manager.submit(
            provider_name='docker',
            project={'name': 'test', 'type': 'web'},
            artifacts={},
            config=config,
        )
        job = DeploymentJob.objects.get(deployment_id=deployment_id)
        self.assertEqual(job.config_data, config)

    def test_get_status_unknown(self):
        self.assertIsNone(self.manager.get_status(str(uuid.uuid4())))

    def test_list_jobs_empty(self):
        jobs = self.manager.list_jobs()
        self.assertEqual(jobs, {})

    def test_list_jobs_after_submit(self):
        did = self.manager.submit(
            provider_name='docker',
            project={'name': 'test', 'type': 'web'},
            artifacts={},
        )
        jobs = self.manager.list_jobs()
        self.assertIn(did, jobs)

    def test_cancel_nonexistent(self):
        self.manager.cancel(str(uuid.uuid4()))

    def test_properties(self):
        self.assertIsNotNone(self.manager.backend)
        self.assertIsNotNone(self.manager.event_bus)
        self.assertIsNotNone(self.manager.monitor)

    def test_submit_multiple_jobs(self):
        did1 = self.manager.submit(
            provider_name='docker',
            project={'name': 'app1', 'type': 'web'},
            artifacts={},
        )
        did2 = self.manager.submit(
            provider_name='proxmox',
            project={'name': 'app2', 'type': 'api'},
            artifacts={},
        )
        self.assertNotEqual(did1, did2)
        self.assertEqual(DeploymentJob.objects.count(), 2)
