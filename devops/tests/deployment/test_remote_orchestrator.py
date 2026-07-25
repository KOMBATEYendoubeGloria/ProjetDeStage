"""Tests for orchestrator remote validation."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from devops.deployment.exceptions import DeploymentValidationError
from devops.deployment.monitoring.deployment_monitor import DeploymentMonitor
from devops.deployment.orchestrator.deployment_orchestrator import DeploymentOrchestrator


class OrchestratorRemoteValidationTests(SimpleTestCase):

    def _make_orchestrator(self):
        return DeploymentOrchestrator(monitoring=DeploymentMonitor())

    def test_validate_local_config_passes(self):
        o = self._make_orchestrator()
        o._validate({'name': 'app'}, {'dockerfile': 'FROM alpine'}, {})
        o._validate({'name': 'app'}, {'dockerfile': 'FROM alpine'}, None)

    def test_validate_remote_config_valid(self):
        o = self._make_orchestrator()
        config = {'host': '10.0.0.1', 'ssh_user': 'root'}
        o._validate({'name': 'app'}, {'dockerfile': 'FROM alpine'}, config)

    def test_validate_remote_config_missing_host(self):
        o = self._make_orchestrator()
        config = {'ssh_user': 'root'}
        o._validate({'name': 'app'}, {'dockerfile': 'FROM alpine'}, config)

    def test_validate_remote_config_missing_username(self):
        o = self._make_orchestrator()
        config = {'host': '10.0.0.1', 'deployment_target_id': 1}
        o._validate({'name': 'app'}, {'dockerfile': 'FROM alpine'}, config)

    def test_validate_deployment_target_id_resolves_none_skips(self):
        o = self._make_orchestrator()
        config = {'deployment_target_id': 1}
        o._validate({'name': 'app'}, {'dockerfile': 'FROM alpine'}, config)
