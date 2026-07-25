"""Tests for DeploymentService (service layer facade)."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from devops.deployment.orchestrator.deployment_orchestrator import DeploymentOrchestrator
from devops.deployment.providers.base import ProviderRegistry
from devops.deployment.services import DeploymentService


class DeploymentServiceTests(SimpleTestCase):

    def test_init_with_custom_orchestrator(self):
        orch = MagicMock(spec=DeploymentOrchestrator)
        svc = DeploymentService(orchestrator=orch)
        self.assertIs(svc.orchestrator, orch)

    def test_init_default_orchestrator(self):
        svc = DeploymentService()
        self.assertIsInstance(svc.orchestrator, DeploymentOrchestrator)

    def test_start_delegation(self):
        orch = MagicMock(spec=DeploymentOrchestrator)
        orch.deploy.return_value = MagicMock(status='SUCCESS')
        svc = DeploymentService(orchestrator=orch)
        result = svc.start_deployment(
            'docker', {'name': 'app'}, {'dockerfile': 'FROM alpine'}
        )
        orch.deploy.assert_called_once_with(
            'docker', {'name': 'app'}, {'dockerfile': 'FROM alpine'}, None
        )

    def test_teardown_delegation(self):
        orch = MagicMock(spec=DeploymentOrchestrator)
        orch.teardown.return_value = MagicMock(status='SUCCESS')
        svc = DeploymentService(orchestrator=orch)
        svc.teardown('docker', {'name': 'app'})
        orch.teardown.assert_called_once()

    def test_status_delegation(self):
        orch = MagicMock(spec=DeploymentOrchestrator)
        orch.status.return_value = {'status': 'active'}
        svc = DeploymentService(orchestrator=orch)
        result = svc.status('docker', {'name': 'app'})
        self.assertEqual(result['status'], 'active')

    def test_available_providers(self):
        old = ProviderRegistry._registry.copy()
        try:
            from devops.deployment.providers.docker_provider import DockerProvider
            ProviderRegistry.register(DockerProvider)
            providers = DeploymentService.available_providers()
            self.assertIn('docker', providers)
        finally:
            ProviderRegistry._registry = old
