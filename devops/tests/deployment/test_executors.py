"""Tests for Terraform, Ansible, and Docker executors — all subprocess calls mocked."""

import json
from unittest.mock import MagicMock, mock_open, patch

from django.test import SimpleTestCase

from devops.deployment.exceptions import (
    AnsibleExecutorError,
    DockerExecutorError,
    TerraformExecutorError,
)
from devops.deployment.executors.ansible_executor import AnsibleExecutor
from devops.deployment.executors.base import BaseExecutor
from devops.deployment.executors.docker_executor import DockerExecutor
from devops.deployment.executors.terraform_executor import TerraformExecutor


# ---------------------------------------------------------------------------
# BaseExecutor
# ---------------------------------------------------------------------------

class BaseExecutorTests(SimpleTestCase):

    def test_cannot_instantiate_abc(self):
        with self.assertRaises(TypeError):
            BaseExecutor()


# ---------------------------------------------------------------------------
# TerraformExecutor
# ---------------------------------------------------------------------------

class TerraformExecutorTests(SimpleTestCase):

    def test_executor_name(self):
        t = TerraformExecutor()
        self.assertEqual(t.executor_name, 'terraform')

    def test_is_base_executor(self):
        self.assertTrue(issubclass(TerraformExecutor, BaseExecutor))

    def test_initialize_no_subprocess(self):
        t = TerraformExecutor()
        result = t.initialize('/tmp/w')
        self.assertEqual(result, {'status': 'initialized'})

    @patch('devops.deployment.executors.terraform_executor.subprocess.run')
    def test_execute_writes_artifacts_and_runs(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='{}', stderr='')
        t = TerraformExecutor()
        result = t.execute('/tmp/w', {'terraform': 'resource "null_resource" "test" {}'})
        self.assertEqual(result['status'], 'applied')
        self.assertEqual(mock_run.call_count, 4)

    @patch('devops.deployment.executors.terraform_executor.subprocess.run')
    def test_execute_empty_artifacts_raises(self, mock_run):
        t = TerraformExecutor()
        with self.assertRaises(TerraformExecutorError):
            t.execute('/tmp/w', {})

    @patch('devops.deployment.executors.terraform_executor.subprocess.run')
    def test_execute_failure_raises(self, mock_run):
        mock_run.side_effect = TerraformExecutorError('apply failed')
        t = TerraformExecutor()
        with self.assertRaises(TerraformExecutorError):
            t.execute('/tmp/w', {'terraform': 'resource {}'})

    @patch('devops.deployment.executors.terraform_executor.subprocess.run')
    def test_teardown_runs_destroy(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
        t = TerraformExecutor()
        result = t.teardown('/tmp/w')
        self.assertEqual(result['status'], 'destroyed')
        mock_run.assert_called_once()

    @patch('devops.deployment.executors.terraform_executor.subprocess.run')
    def test_validate(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
        t = TerraformExecutor()
        self.assertTrue(t.validate('/tmp/w'))

    def test_get_logs_returns_list(self):
        t = TerraformExecutor()
        logs = t.get_logs()
        self.assertIsInstance(logs, list)


# ---------------------------------------------------------------------------
# AnsibleExecutor
# ---------------------------------------------------------------------------

class AnsibleExecutorTests(SimpleTestCase):

    def test_executor_name(self):
        a = AnsibleExecutor()
        self.assertEqual(a.executor_name, 'ansible')

    def test_is_base_executor(self):
        self.assertTrue(issubclass(AnsibleExecutor, BaseExecutor))

    @patch('devops.deployment.executors.ansible_executor.subprocess.run')
    def test_execute_writes_playbook_and_runs(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
        a = AnsibleExecutor()
        artifacts = {'ansible_playbook': '---\n- hosts: all', 'ansible_inventory': 'localhost ansible_connection=local'}
        m = mock_open()
        with patch('builtins.open', m):
            result = a.execute('/tmp/w', artifacts)
        self.assertEqual(result['status'], 'configured')
        mock_run.assert_called_once()

    def test_execute_no_playbook_raises(self):
        a = AnsibleExecutor()
        with self.assertRaises(AnsibleExecutorError):
            a.execute('/tmp/w', {})

    @patch('devops.deployment.executors.ansible_executor.subprocess.run')
    def test_execute_failure_raises(self, mock_run):
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(2, 'ansible-playbook', stderr='play failed')
        a = AnsibleExecutor()
        m = mock_open()
        with patch('builtins.open', m):
            with self.assertRaises(AnsibleExecutorError):
                a.execute('/tmp/w', {'ansible_playbook': '---\n- hosts: all'})

    def test_teardown_is_noop(self):
        a = AnsibleExecutor()
        result = a.teardown('/tmp/w')
        self.assertEqual(result['status'], 'no_op')


# ---------------------------------------------------------------------------
# DockerExecutor
# ---------------------------------------------------------------------------

class DockerExecutorTests(SimpleTestCase):

    def test_executor_name(self):
        d = DockerExecutor()
        self.assertEqual(d.executor_name, 'docker')

    def test_is_base_executor(self):
        self.assertTrue(issubclass(DockerExecutor, BaseExecutor))

    @patch('devops.deployment.executors.docker_executor.subprocess.run')
    def test_execute_compose_up(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='done', stderr='')
        d = DockerExecutor()
        artifacts = {'docker_compose': 'version: "3"'}
        m = mock_open()
        with patch('builtins.open', m):
            result = d.execute('/tmp/w', artifacts)
        self.assertEqual(result['status'], 'deployed')
        self.assertIn('compose_output', result)

    @patch('devops.deployment.executors.docker_executor.subprocess.run')
    def test_execute_build_and_run(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='container-id', stderr='')
        d = DockerExecutor()
        artifacts = {'dockerfile': 'FROM alpine'}
        m = mock_open()
        with patch('builtins.open', m):
            result = d.execute('/tmp/w', artifacts)
        self.assertEqual(result['status'], 'deployed')
        self.assertIn('container_id', result)

    def test_execute_no_artifacts_raises(self):
        d = DockerExecutor()
        with self.assertRaises(DockerExecutorError):
            d.execute('/tmp/w', {})

    @patch('devops.deployment.executors.docker_executor.subprocess.run')
    def test_execute_failure_raises(self, mock_run):
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(1, 'docker', stderr='build failed')
        d = DockerExecutor()
        m = mock_open()
        with patch('builtins.open', m):
            with self.assertRaises(DockerExecutorError):
                d.execute('/tmp/w', {'dockerfile': 'FROM alpine'})

    @patch('devops.deployment.executors.docker_executor.subprocess.run')
    def test_teardown_compose_down(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
        d = DockerExecutor()
        result = d.teardown('/tmp/w')
        self.assertEqual(result['status'], 'stopped')

    @patch('devops.deployment.executors.docker_executor.subprocess.run')
    def test_teardown_failure_attempts_cleanup(self, mock_run):
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(1, 'docker', stderr='no compose file')
        d = DockerExecutor()
        result = d.teardown('/tmp/w')
        self.assertEqual(result['status'], 'cleanup_attempted')

    def test_get_logs_returns_list(self):
        d = DockerExecutor()
        logs = d.get_logs()
        self.assertIsInstance(logs, list)
