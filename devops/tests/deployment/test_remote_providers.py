"""Tests for providers with remote mode — all SSH calls mocked."""

from unittest.mock import MagicMock, mock_open, patch

from django.test import SimpleTestCase

from devops.deployment.exceptions import ProviderError
from devops.deployment.providers.docker_provider import DockerProvider
from devops.deployment.providers.proxmox_provider import ProxmoxProvider
from devops.deployment.providers.virtualbox_provider import VirtualBoxProvider
from devops.deployment.providers.vmware_provider import VMwareProvider


REMOTE_CONFIG = {
    'host': '10.0.0.1',
    'ssh_user': 'root',
    'ssh_key': 'PRIVATE_KEY',
    'remote_workspace': '/opt/deploy',
}


class DockerProviderRemoteTests(SimpleTestCase):

    @patch('devops.deployment.providers.docker_provider.connect_ssh')
    @patch('devops.deployment.providers.docker_provider.create_ssh_command_runner')
    @patch('devops.deployment.providers.docker_provider.transfer_artifacts_to_remote')
    @patch('devops.deployment.providers.docker_provider.DockerExecutor')
    def test_deploy_remote(self, MockExec, mock_transfer, mock_runner, mock_connect):
        mock_ssh = MagicMock()
        mock_connect.return_value = mock_ssh
        mock_runner.return_value = MagicMock()
        MockExec.return_value.execute.return_value = {'status': 'deployed'}
        p = DockerProvider()
        result = p.deploy({'name': 'app'}, {'dockerfile': 'FROM alpine'}, REMOTE_CONFIG)
        self.assertEqual(result['status'], 'deployed')
        mock_connect.assert_called_once()
        MockExec.return_value.execute.assert_called_once()

    @patch('devops.deployment.providers.docker_provider.connect_ssh')
    @patch('devops.deployment.providers.docker_provider.create_ssh_command_runner')
    @patch('devops.deployment.providers.docker_provider.transfer_artifacts_to_remote')
    @patch('devops.deployment.providers.docker_provider.DockerExecutor')
    def test_deploy_remote_failure(self, MockExec, mock_transfer, mock_runner, mock_connect):
        mock_connect.return_value = MagicMock()
        mock_runner.return_value = MagicMock()
        MockExec.return_value.execute.side_effect = RuntimeError('boom')
        p = DockerProvider()
        with self.assertRaises(ProviderError):
            p.deploy({'name': 'app'}, {'dockerfile': 'FROM alpine'}, REMOTE_CONFIG)

    @patch('devops.deployment.providers.docker_provider.connect_ssh')
    @patch('devops.deployment.providers.docker_provider.create_ssh_command_runner')
    @patch('devops.deployment.providers.docker_provider.DockerExecutor')
    def test_teardown_remote(self, MockExec, mock_runner, mock_connect):
        mock_connect.return_value = MagicMock()
        mock_runner.return_value = MagicMock()
        MockExec.return_value.teardown.return_value = {'status': 'stopped'}
        p = DockerProvider()
        result = p.teardown({'name': 'app'}, REMOTE_CONFIG)
        self.assertEqual(result['status'], 'stopped')


class ProxmoxProviderRemoteTests(SimpleTestCase):

    @patch('devops.deployment.providers.proxmox_provider.connect_ssh')
    @patch('devops.deployment.providers.proxmox_provider.create_ssh_command_runner')
    @patch('devops.deployment.providers.proxmox_provider.transfer_artifacts_to_remote')
    @patch('devops.deployment.providers.proxmox_provider.AnsibleExecutor')
    @patch('devops.deployment.providers.proxmox_provider.DockerExecutor')
    def test_deploy_remote_full_pipeline(self, MockDocker, MockAnsible, mock_transfer, mock_runner, mock_connect):
        mock_connect.return_value = MagicMock()
        mock_runner.return_value = MagicMock()
        MockAnsible.return_value.execute.return_value = {'status': 'ok'}
        MockDocker.return_value.execute.return_value = {'status': 'deployed'}
        p = ProxmoxProvider()
        result = p.deploy(
            {'name': 'app'},
            {'ansible_playbook': '---', 'dockerfile': 'FROM alpine'},
            REMOTE_CONFIG,
        )
        self.assertEqual(result['status'], 'deployed')
        MockAnsible.return_value.execute.assert_called_once()
        MockDocker.return_value.execute.assert_called_once()

    @patch('devops.deployment.providers.proxmox_provider.connect_ssh')
    @patch('devops.deployment.providers.proxmox_provider.create_ssh_command_runner')
    @patch('devops.deployment.providers.proxmox_provider.transfer_artifacts_to_remote')
    @patch('devops.deployment.providers.proxmox_provider.DockerExecutor')
    def test_deploy_remote_docker_failure(self, MockDocker, mock_transfer, mock_runner, mock_connect):
        mock_connect.return_value = MagicMock()
        mock_runner.return_value = MagicMock()
        MockDocker.return_value.execute.side_effect = RuntimeError('deploy failed')
        p = ProxmoxProvider()
        with self.assertRaises(ProviderError):
            p.deploy(
                {'name': 'app'},
                {'dockerfile': 'FROM alpine'},
                REMOTE_CONFIG,
            )


class VMwareProviderRemoteTests(SimpleTestCase):

    @patch('devops.deployment.providers.vmware_provider.connect_ssh')
    @patch('devops.deployment.providers.vmware_provider.create_ssh_command_runner')
    @patch('devops.deployment.providers.vmware_provider.transfer_artifacts_to_remote')
    @patch('devops.deployment.providers.vmware_provider.AnsibleExecutor')
    @patch('devops.deployment.providers.vmware_provider.DockerExecutor')
    def test_deploy_remote_full_pipeline(self, MockDocker, MockAnsible, mock_transfer, mock_runner, mock_connect):
        mock_connect.return_value = MagicMock()
        mock_runner.return_value = MagicMock()
        MockAnsible.return_value.execute.return_value = {'status': 'ok'}
        MockDocker.return_value.execute.return_value = {'status': 'deployed'}
        p = VMwareProvider()
        result = p.deploy(
            {'name': 'app'},
            {'ansible_playbook': '---', 'dockerfile': 'FROM alpine'},
            REMOTE_CONFIG,
        )
        self.assertEqual(result['status'], 'deployed')


class VirtualBoxProviderRemoteTests(SimpleTestCase):

    @patch('devops.deployment.providers.virtualbox_provider.connect_ssh')
    @patch('devops.deployment.providers.virtualbox_provider.create_ssh_command_runner')
    @patch('devops.deployment.providers.virtualbox_provider.transfer_artifacts_to_remote')
    @patch('devops.deployment.providers.virtualbox_provider.AnsibleExecutor')
    @patch('devops.deployment.providers.virtualbox_provider.DockerExecutor')
    def test_deploy_remote_full_pipeline(self, MockDocker, MockAnsible, mock_transfer, mock_runner, mock_connect):
        mock_connect.return_value = MagicMock()
        mock_runner.return_value = MagicMock()
        MockAnsible.return_value.execute.return_value = {'status': 'ok'}
        MockDocker.return_value.execute.return_value = {'status': 'deployed'}
        p = VirtualBoxProvider()
        result = p.deploy(
            {'name': 'app'},
            {'ansible_playbook': '---', 'dockerfile': 'FROM alpine'},
            REMOTE_CONFIG,
        )
        self.assertEqual(result['status'], 'deployed')
