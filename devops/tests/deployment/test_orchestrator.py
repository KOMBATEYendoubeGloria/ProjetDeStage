"""Tests for DeploymentOrchestrator."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from devops.deployment.exceptions import (
    DeploymentEngineError,
    DeploymentValidationError,
    RollbackError,
)
from devops.deployment.monitoring.deployment_monitor import DeploymentMonitor
from devops.deployment.orchestrator.deployment_orchestrator import DeploymentOrchestrator
from devops.deployment.providers.docker_provider import DockerProvider
from devops.deployment.result import DeploymentResult


class DeploymentOrchestratorTests(SimpleTestCase):

    def _make_orchestrator(self):
        return DeploymentOrchestrator(monitoring=DeploymentMonitor())

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def test_validate_empty_project(self):
        o = self._make_orchestrator()
        with self.assertRaises(DeploymentValidationError):
            o._validate({}, {})

    def test_validate_empty_artifacts(self):
        o = self._make_orchestrator()
        with self.assertRaises(DeploymentValidationError):
            o._validate({'name': 'app'}, {})

    def test_validate_missing_project_name(self):
        o = self._make_orchestrator()
        with self.assertRaises(DeploymentValidationError):
            o._validate({'other': 'value'}, {'dockerfile': 'FROM alpine'})

    # ------------------------------------------------------------------
    # Happy path
    # ------------------------------------------------------------------

    @patch('devops.deployment.orchestrator.deployment_orchestrator.ProviderRegistry')
    def test_deploy_success(self, MockRegistry):
        provider = MagicMock(spec=DockerProvider)
        provider.provision.return_value = {'status': 'provisioned'}
        provider.deploy.return_value = {'status': 'deployed'}
        MockRegistry.create.return_value = provider

        o = self._make_orchestrator()
        result = o.deploy(
            'docker',
            {'name': 'my-app'},
            {'dockerfile': 'FROM alpine', 'docker_compose': 'version: "3"'},
        )
        self.assertEqual(result.status, 'SUCCESS')
        provider.provision.assert_called_once()
        provider.deploy.assert_called_once()
        self.assertIn('provision', result.outputs)
        self.assertIn('deploy', result.outputs)

    # ------------------------------------------------------------------
    # Provider not found
    # ------------------------------------------------------------------

    @patch('devops.deployment.orchestrator.deployment_orchestrator.ProviderRegistry')
    def test_deploy_unknown_provider(self, MockRegistry):
        MockRegistry.create.side_effect = ValueError('not found')
        o = self._make_orchestrator()
        result = o.deploy('unknown', {'name': 'app'}, {'dockerfile': 'FROM alpine'})
        self.assertEqual(result.status, 'FAILED')

    # ------------------------------------------------------------------
    # Rollback on failure
    # ------------------------------------------------------------------

    @patch('devops.deployment.orchestrator.deployment_orchestrator.ProviderRegistry')
    def test_deploy_failure_triggers_rollback(self, MockRegistry):
        provider = MagicMock(spec=DockerProvider)
        provider.provision.return_value = {'status': 'ok'}
        provider.deploy.side_effect = DeploymentEngineError('deploy failed')
        provider.teardown.return_value = {'status': 'rolled-back'}
        MockRegistry.create.return_value = provider

        o = self._make_orchestrator()
        result = o.deploy(
            'docker',
            {'name': 'my-app'},
            {'dockerfile': 'FROM alpine'},
        )
        self.assertEqual(result.status, 'FAILED')
        provider.teardown.assert_called_once()
        self.assertTrue(any('Rollback completed' in log for log in result.logs))

    @patch('devops.deployment.orchestrator.deployment_orchestrator.ProviderRegistry')
    def test_rollback_failure_does_not_propagate(self, MockRegistry):
        provider = MagicMock(spec=DockerProvider)
        provider.provision.return_value = {}
        provider.deploy.side_effect = DeploymentEngineError('fail')
        provider.teardown.side_effect = RuntimeError('rollback boom')
        MockRegistry.create.return_value = provider

        o = self._make_orchestrator()
        result = o.deploy('docker', {'name': 'app'}, {'dockerfile': 'FROM alpine'})
        self.assertEqual(result.status, 'FAILED')
        self.assertTrue(any('Rollback failed' in log for log in result.logs))

    # ------------------------------------------------------------------
    # Teardown
    # ------------------------------------------------------------------

    @patch('devops.deployment.orchestrator.deployment_orchestrator.ProviderRegistry')
    def test_teardown_success(self, MockRegistry):
        provider = MagicMock(spec=DockerProvider)
        provider.teardown.return_value = {'status': 'destroyed'}
        MockRegistry.create.return_value = provider

        o = self._make_orchestrator()
        result = o.teardown('docker', {'name': 'app'})
        self.assertEqual(result.status, 'SUCCESS')

    @patch('devops.deployment.orchestrator.deployment_orchestrator.ProviderRegistry')
    def test_teardown_failure(self, MockRegistry):
        provider = MagicMock(spec=DockerProvider)
        provider.teardown.side_effect = RuntimeError('boom')
        MockRegistry.create.return_value = provider

        o = self._make_orchestrator()
        result = o.teardown('docker', {'name': 'app'})
        self.assertEqual(result.status, 'FAILED')

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    @patch('devops.deployment.orchestrator.deployment_orchestrator.ProviderRegistry')
    def test_status(self, MockRegistry):
        provider = MagicMock(spec=DockerProvider)
        provider.status.return_value = {'provider': 'docker', 'status': 'active'}
        MockRegistry.create.return_value = provider

        o = self._make_orchestrator()
        result = o.status('docker', {'name': 'app'})
        self.assertEqual(result['status'], 'active')
