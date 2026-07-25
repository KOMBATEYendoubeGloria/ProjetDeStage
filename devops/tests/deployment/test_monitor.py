"""Tests for DeploymentMonitor."""

from django.test import SimpleTestCase

from devops.deployment.monitoring.deployment_monitor import DeploymentMonitor
from devops.deployment.result import DeploymentResult


class DeploymentMonitorTests(SimpleTestCase):

    def test_track_and_get_status(self):
        monitor = DeploymentMonitor()
        r = DeploymentResult(deployment_id='d1', provider='docker')
        monitor.track('d1', r)
        status = monitor.get_status('d1')
        self.assertIsNotNone(status)
        self.assertEqual(status['deployment_id'], 'd1')
        self.assertEqual(status['phase'], 'initializing')

    def test_update_phase(self):
        monitor = DeploymentMonitor()
        r = DeploymentResult(deployment_id='d2')
        monitor.track('d2', r)
        monitor.update_phase('d2', 'provisioning')
        status = monitor.get_status('d2')
        self.assertEqual(status['phase'], 'provisioning')
        self.assertIn('initializing', status['history'])
        self.assertIn('provisioning', status['history'])

    def test_get_status_unknown(self):
        monitor = DeploymentMonitor()
        self.assertIsNone(monitor.get_status('unknown'))

    def test_update_phase_unknown_does_not_raise(self):
        monitor = DeploymentMonitor()
        monitor.update_phase('nonexistent', 'deploying')

    def test_list_deployments(self):
        monitor = DeploymentMonitor()
        monitor.track('d1', DeploymentResult(deployment_id='d1'))
        monitor.track('d2', DeploymentResult(deployment_id='d2'))
        monitor.update_phase('d2', 'completed')
        listing = monitor.list_deployments()
        self.assertEqual(listing, {'d1': 'initializing', 'd2': 'completed'})

    def test_multiple_transitions(self):
        monitor = DeploymentMonitor()
        monitor.track('d3', DeploymentResult(deployment_id='d3'))
        for phase in ['provisioning', 'deploying', 'completed']:
            monitor.update_phase('d3', phase)
        status = monitor.get_status('d3')
        self.assertEqual(status['phase'], 'completed')
        self.assertEqual(status['history'], ['initializing', 'provisioning', 'deploying', 'completed'])
