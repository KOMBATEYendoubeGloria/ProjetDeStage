"""Tests for PersistentDeploymentMonitor."""

import uuid

from django.test import TestCase, override_settings

from devops.deployment.events.event_bus import EventBus
from devops.deployment.monitoring.persistent_monitor import PersistentDeploymentMonitor
from devops.models import DeploymentJob, DeploymentLogEntry, DeploymentStageProgress, DeploymentEvent


@override_settings(SECURE_SSL_REDIRECT=False)
class PersistentDeploymentMonitorTests(TestCase):

    def setUp(self):
        self.event_bus = EventBus()
        self.monitor = PersistentDeploymentMonitor(event_bus=self.event_bus)

    def _make_id(self):
        return str(uuid.uuid4())

    def test_track_creates_job(self):
        did = self._make_id()
        self.monitor.track(did)
        job = DeploymentJob.objects.get(deployment_id=did)
        self.assertEqual(job.status, DeploymentJob.Status.RUNNING)
        self.assertIsNotNone(job.started_at)

    def test_track_unknown_returns_gracefully(self):
        # Should not raise even if called twice
        did = self._make_id()
        self.monitor.track(did)
        self.monitor.track(did)  # second call is fine

    def test_update_phase_unknown_does_not_raise(self):
        self.monitor.update_phase('nonexistent', 'provisioning')

    def test_update_phase_creates_stage_progress(self):
        did = self._make_id()
        self.monitor.track(did)
        self.monitor.update_phase(did, 'provisioning')
        sp = DeploymentStageProgress.objects.filter(
            job__deployment_id=did, stage_name='PROVISIONING'
        ).first()
        self.assertIsNotNone(sp)
        self.assertEqual(sp.status, 'RUNNING')

    def test_update_phase_updates_progress_percent(self):
        did = self._make_id()
        self.monitor.track(did)
        self.monitor.mark_stage_completed(did, 'VALIDATION')
        job = DeploymentJob.objects.get(deployment_id=did)
        self.assertEqual(job.progress_percent, 5)

    def test_mark_stage_completed(self):
        did = self._make_id()
        self.monitor.track(did)
        self.monitor.mark_stage_completed(did, 'VALIDATION')
        sp = DeploymentStageProgress.objects.filter(
            job__deployment_id=did, stage_name='VALIDATION'
        ).first()
        self.assertEqual(sp.status, 'COMPLETED')
        self.assertIsNotNone(sp.finished_at)

    def test_mark_completed(self):
        did = self._make_id()
        self.monitor.track(did)
        self.monitor.mark_completed(did)
        job = DeploymentJob.objects.get(deployment_id=did)
        self.assertEqual(job.status, DeploymentJob.Status.COMPLETED)
        self.assertEqual(job.progress_percent, 100)

    def test_mark_failed(self):
        did = self._make_id()
        self.monitor.track(did)
        self.monitor.mark_failed(did, 'something broke')
        job = DeploymentJob.objects.get(deployment_id=did)
        self.assertEqual(job.status, DeploymentJob.Status.FAILED)
        self.assertEqual(job.error_message, 'something broke')

    def test_mark_cancelled(self):
        did = self._make_id()
        self.monitor.track(did)
        self.monitor.mark_cancelled(did)
        job = DeploymentJob.objects.get(deployment_id=did)
        self.assertEqual(job.status, DeploymentJob.Status.CANCELLED)

    def test_add_log(self):
        did = self._make_id()
        self.monitor.track(did)
        self.monitor.add_log(did, 'Hello world', level='WARNING', stage='VALIDATION')
        log = DeploymentLogEntry.objects.filter(job__deployment_id=did).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.message, 'Hello world')
        self.assertEqual(log.level, 'WARNING')
        self.assertEqual(log.stage, 'VALIDATION')

    def test_add_log_unknown_does_not_raise(self):
        self.monitor.add_log('nonexistent', 'msg')

    def test_add_event(self):
        did = self._make_id()
        self.monitor.track(did)
        self.monitor.add_event(did, 'custom_event', {'foo': 'bar'})
        event = DeploymentEvent.objects.filter(job__deployment_id=did).first()
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, 'custom_event')
        self.assertEqual(event.payload, {'foo': 'bar'})

    def test_add_event_unknown_does_not_raise(self):
        self.monitor.add_event('nonexistent', 'ev')

    def test_get_status(self):
        did = self._make_id()
        self.monitor.track(did)
        status = self.monitor.get_status(did)
        self.assertIsNotNone(status)
        self.assertEqual(status['deployment_id'], did)
        self.assertIn('stages', status)

    def test_get_status_unknown(self):
        self.assertIsNone(self.monitor.get_status('nonexistent'))

    def test_list_deployments(self):
        did1 = self._make_id()
        did2 = self._make_id()
        self.monitor.track(did1)
        self.monitor.track(did2)
        listing = self.monitor.list_deployments()
        self.assertIn(did1, listing)
        self.assertIn(did2, listing)

    def test_event_bus_publishes_on_track(self):
        received = []
        self.event_bus.subscribe('deployment.started', lambda t, p: received.append(p))
        did = self._make_id()
        self.monitor.track(did)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['deployment_id'], did)

    def test_event_bus_publishes_on_complete(self):
        received = []
        self.event_bus.subscribe('deployment.completed', lambda t, p: received.append(p))
        did = self._make_id()
        self.monitor.track(did)
        self.monitor.mark_completed(did)
        self.assertEqual(len(received), 1)
