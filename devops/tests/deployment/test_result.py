"""Tests for DeploymentResult data structure."""

from django.test import SimpleTestCase

from devops.deployment.result import DeploymentResult


class DeploymentResultTests(SimpleTestCase):

    def test_default_values(self):
        r = DeploymentResult()
        self.assertEqual(r.status, 'PENDING')
        self.assertEqual(r.provider, '')
        self.assertEqual(r.deployment_id, '')
        self.assertEqual(r.logs, [])
        self.assertIsNone(r.start_time)
        self.assertIsNone(r.end_time)
        self.assertIsNone(r.duration)
        self.assertEqual(r.outputs, {})
        self.assertEqual(r.errors, [])

    def test_mark_started(self):
        r = DeploymentResult()
        r.mark_started()
        self.assertIsNotNone(r.start_time)

    def test_mark_completed(self):
        r = DeploymentResult()
        r.mark_started()
        r.mark_completed()
        self.assertEqual(r.status, 'SUCCESS')
        self.assertIsNotNone(r.end_time)
        self.assertIsNotNone(r.duration)
        self.assertGreaterEqual(r.duration, 0)

    def test_mark_failed(self):
        r = DeploymentResult()
        r.mark_started()
        r.mark_failed('something broke')
        self.assertEqual(r.status, 'FAILED')
        self.assertIn('something broke', r.errors)
        self.assertIsNotNone(r.end_time)
        self.assertIsNotNone(r.duration)

    def test_mark_failed_without_start(self):
        r = DeploymentResult()
        r.mark_failed('early failure')
        self.assertEqual(r.status, 'FAILED')
        self.assertIsNone(r.duration)

    def test_add_log(self):
        r = DeploymentResult()
        r.add_log('step one')
        self.assertEqual(len(r.logs), 1)
        self.assertIn('step one', r.logs[0])
        self.assertIn('[', r.logs[0])

    def test_to_dict(self):
        r = DeploymentResult(provider='docker', deployment_id='abc')
        d = r.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d['provider'], 'docker')
        self.assertEqual(d['deployment_id'], 'abc')

    def test_to_json(self):
        r = DeploymentResult(provider='proxmox')
        j = r.to_json()
        self.assertIsInstance(j, str)
        self.assertIn('"provider": "proxmox"', j)
