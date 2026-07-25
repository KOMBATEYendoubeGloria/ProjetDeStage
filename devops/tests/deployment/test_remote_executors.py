"""Tests for executors with remote command_runner support — all SSH/subprocess mocked."""

from unittest.mock import MagicMock, mock_open, patch

from django.test import SimpleTestCase

from devops.deployment.executors.ansible_executor import AnsibleExecutor
from devops.deployment.executors.docker_executor import DockerExecutor
from devops.deployment.executors.terraform_executor import TerraformExecutor
from devops.deployment.remote.command_runner import SSHCommandRunner


class TerraformExecutorRemoteTests(SimpleTestCase):

    def test_execute_with_ssh_runner(self):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {'stdout': '{}', 'stderr': '', 'exit_code': 0}
        runner = SSHCommandRunner(mock_ssh)
        t = TerraformExecutor()
        result = t.execute('/tmp/w', {'terraform': 'resource "null_resource" "test" {}'}, command_runner=runner)
        self.assertEqual(result['status'], 'applied')
        mock_ssh.execute.assert_called()

    def test_teardown_with_ssh_runner(self):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {'stdout': '', 'stderr': '', 'exit_code': 0}
        runner = SSHCommandRunner(mock_ssh)
        t = TerraformExecutor()
        result = t.teardown('/tmp/w', command_runner=runner)
        self.assertEqual(result['status'], 'destroyed')
        mock_ssh.execute.assert_called()

    def test_no_runner_still_works(self):
        with patch('devops.deployment.executors.terraform_executor.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout='{}', stderr='')
            t = TerraformExecutor()
            result = t.execute('/tmp/w', {'terraform': 'resource {}'})
            self.assertEqual(result['status'], 'applied')


class AnsibleExecutorRemoteTests(SimpleTestCase):

    def test_execute_with_ssh_runner(self):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {'stdout': '', 'stderr': '', 'exit_code': 0}
        runner = SSHCommandRunner(mock_ssh)
        a = AnsibleExecutor()
        artifacts = {'ansible_playbook': '---\n- hosts: all'}
        m = mock_open()
        with patch('builtins.open', m):
            result = a.execute('/tmp/w', artifacts, command_runner=runner)
        self.assertEqual(result['status'], 'configured')
        mock_ssh.execute.assert_called()

    def test_no_runner_still_works(self):
        with patch('devops.deployment.executors.ansible_executor.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
            a = AnsibleExecutor()
            m = mock_open()
            with patch('builtins.open', m):
                result = a.execute('/tmp/w', {'ansible_playbook': '---\n- hosts: all'})
            self.assertEqual(result['status'], 'configured')


class DockerExecutorRemoteTests(SimpleTestCase):

    def test_compose_with_ssh_runner(self):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {'stdout': 'done', 'stderr': '', 'exit_code': 0}
        runner = SSHCommandRunner(mock_ssh)
        d = DockerExecutor()
        m = mock_open()
        with patch('builtins.open', m):
            result = d.execute('/tmp/w', {'docker_compose': 'version: "3"'}, command_runner=runner)
        self.assertEqual(result['status'], 'deployed')
        mock_ssh.execute.assert_called()

    def test_teardown_with_ssh_runner(self):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {'stdout': '', 'stderr': '', 'exit_code': 0}
        runner = SSHCommandRunner(mock_ssh)
        d = DockerExecutor()
        result = d.teardown('/tmp/w', command_runner=runner)
        self.assertEqual(result['status'], 'stopped')
        mock_ssh.execute.assert_called()

    def test_no_runner_still_works(self):
        with patch('devops.deployment.executors.docker_executor.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout='done', stderr='')
            d = DockerExecutor()
            m = mock_open()
            with patch('builtins.open', m):
                result = d.execute('/tmp/w', {'docker_compose': 'version: "3"'})
            self.assertEqual(result['status'], 'deployed')
