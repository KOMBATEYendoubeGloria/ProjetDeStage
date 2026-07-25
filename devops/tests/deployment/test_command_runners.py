"""Tests for CommandRunner implementations — all subprocess calls mocked."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from devops.deployment.exceptions import ExecutorError
from devops.deployment.remote.command_runner import (
    CommandRunner,
    LocalCommandRunner,
    SSHCommandRunner,
)


# ---------------------------------------------------------------------------
# CommandRunner ABC
# ---------------------------------------------------------------------------

class CommandRunnerABCTests(SimpleTestCase):

    def test_cannot_instantiate_abc(self):
        with self.assertRaises(TypeError):
            CommandRunner()


# ---------------------------------------------------------------------------
# LocalCommandRunner
# ---------------------------------------------------------------------------

class LocalCommandRunnerTests(SimpleTestCase):

    @patch('devops.deployment.remote.command_runner.subprocess.run')
    def test_run_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='hello', stderr='')
        runner = LocalCommandRunner()
        result = runner.run(['echo', 'hello'])
        self.assertEqual(result, 'hello')

    @patch('devops.deployment.remote.command_runner.subprocess.run')
    def test_run_failure_raises(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout='', stderr='error occurred')
        runner = LocalCommandRunner()
        with self.assertRaises(ExecutorError):
            runner.run(['bad', 'command'])

    @patch('devops.deployment.remote.command_runner.subprocess.run')
    def test_run_raw_returns_dict(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='out', stderr='err')
        runner = LocalCommandRunner()
        result = runner.run_raw(['cmd'])
        self.assertEqual(result, {'stdout': 'out', 'stderr': 'err', 'exit_code': 0})

    @patch('devops.deployment.remote.command_runner.subprocess.run')
    def test_run_raw_failure_has_exit_code(self, mock_run):
        mock_run.return_value = MagicMock(returncode=42, stdout='', stderr='fail')
        runner = LocalCommandRunner()
        result = runner.run_raw(['cmd'])
        self.assertEqual(result['exit_code'], 42)

    @patch('devops.deployment.remote.command_runner.subprocess.run')
    def test_file_not_found_raises(self, mock_run):
        mock_run.side_effect = FileNotFoundError
        runner = LocalCommandRunner()
        with self.assertRaises(ExecutorError):
            runner.run(['nonexistent'])

    @patch('devops.deployment.remote.command_runner.subprocess.run')
    def test_cwd_forwarded(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
        runner = LocalCommandRunner()
        runner.run(['cmd'], cwd='/tmp')
        call_kwargs = mock_run.call_args[1]
        self.assertEqual(call_kwargs['cwd'], '/tmp')

    def test_binary_prefix(self):
        runner = LocalCommandRunner(binary_prefix='/usr/bin/env')
        self.assertEqual(runner._prefix, '/usr/bin/env')

    @patch('devops.deployment.remote.command_runner.subprocess.run')
    def test_binary_prefix_prepended(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
        runner = LocalCommandRunner(binary_prefix='sudo')
        runner.run(['terraform', 'plan'])
        cmd_used = mock_run.call_args[0][0]
        self.assertEqual(cmd_used[0], 'sudo')

    def test_get_logs_returns_list(self):
        runner = LocalCommandRunner()
        self.assertIsInstance(runner.get_logs(), list)


# ---------------------------------------------------------------------------
# SSHCommandRunner
# ---------------------------------------------------------------------------

class SSHCommandRunnerTests(SimpleTestCase):

    def test_run_success(self):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {'stdout': 'remote output', 'stderr': '', 'exit_code': 0}
        runner = SSHCommandRunner(mock_ssh)
        result = runner.run(['ls', '-la'])
        self.assertEqual(result, 'remote output')
        mock_ssh.execute.assert_called_once()

    def test_run_failure_raises(self):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {'stdout': '', 'stderr': 'permission denied', 'exit_code': 1}
        runner = SSHCommandRunner(mock_ssh)
        with self.assertRaises(ExecutorError):
            runner.run(['cat', '/etc/shadow'])

    def test_run_raw_returns_dict(self):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {'stdout': 'ok', 'stderr': 'warn', 'exit_code': 0}
        runner = SSHCommandRunner(mock_ssh)
        result = runner.run_raw(['docker', 'ps'])
        self.assertEqual(result, {'stdout': 'ok', 'stderr': 'warn', 'exit_code': 0})

    def test_cwd_prepends_cd(self):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {'stdout': '', 'stderr': '', 'exit_code': 0}
        runner = SSHCommandRunner(mock_ssh)
        runner.run(['ls'], cwd='/opt/app')
        cmd_sent = mock_ssh.execute.call_args[0][0]
        self.assertIn('cd /opt/app', cmd_sent)

    def test_no_cwd_no_cd(self):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {'stdout': '', 'stderr': '', 'exit_code': 0}
        runner = SSHCommandRunner(mock_ssh)
        runner.run(['ls'])
        cmd_sent = mock_ssh.execute.call_args[0][0]
        self.assertNotIn('cd', cmd_sent)

    def test_get_logs_returns_list(self):
        mock_ssh = MagicMock()
        runner = SSHCommandRunner(mock_ssh)
        self.assertIsInstance(runner.get_logs(), list)
