import io
import json
import subprocess
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from devops.exceptions import ContainerException, InfrastructureException, SSHException
from devops.services.implementations.container.docker import DockerService
from devops.services.implementations.infrastructure.base import BaseInfrastructureService
from devops.services.implementations.infrastructure.terraform_service import TerraformService


class ContainerServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = DockerService()

    @patch('devops.services.implementations.container.base.subprocess.run')
    def test_list_containers(self, run_mock):
        run_mock.return_value.stdout = '{"ID":"abc","Names":"/test"}\n'
        run_mock.return_value.returncode = 0
        containers = self.service.list_containers()
        self.assertEqual(containers[0]['ID'], 'abc')

    @patch('devops.services.implementations.container.base.subprocess.run')
    def test_list_images(self, run_mock):
        run_mock.return_value.stdout = '{"Repository":"busybox","Tag":"latest"}\n'
        run_mock.return_value.returncode = 0
        images = self.service.list_images()
        self.assertEqual(images[0]['Repository'], 'busybox')

    @patch('devops.services.implementations.container.base.subprocess.run')
    def test_get_container(self, run_mock):
        run_mock.return_value.stdout = '[{"Id":"abc"}]'
        run_mock.return_value.returncode = 0
        container = self.service.get_container('abc')
        self.assertEqual(container['Id'], 'abc')

    @patch('devops.services.implementations.container.base.subprocess.run')
    def test_create_and_manage_container(self, run_mock):
        run_mock.return_value.stdout = 'container123'
        run_mock.return_value.returncode = 0
        container_id = self.service.create_container('busybox', name='test', command='echo hello')
        self.assertEqual(container_id, 'container123')

    @patch('devops.services.implementations.container.base.subprocess.run')
    def test_container_exception_on_missing_executable(self, run_mock):
        run_mock.side_effect = FileNotFoundError()
        with self.assertRaises(ContainerException):
            self.service.list_images()


class InfrastructureServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = TerraformService()

    @patch('devops.services.implementations.infrastructure.base.subprocess.run')
    def test_validate_calls_binary(self, run_mock):
        run_mock.return_value.stdout = ''
        run_mock.return_value.returncode = 0
        self.service.validate('/tmp/workspace')
        run_mock.assert_called_once()

    @patch('devops.services.implementations.infrastructure.base.subprocess.run')
    def test_plan_returns_parsed_plan(self, run_mock):
        run_mock.return_value.stdout = 'plan output'
        run_mock.return_value.returncode = 0
        result = self.service.plan('/tmp/workspace')
        self.assertEqual(result, {'plan': 'plan output'})

    @patch('devops.services.implementations.infrastructure.base.subprocess.run')
    def test_output_parses_json(self, run_mock):
        run_mock.return_value.stdout = '{"key": "value"}'
        run_mock.return_value.returncode = 0
        result = self.service.output('/tmp/workspace')
        self.assertEqual(result, {'key': 'value'})

    def test_workspace_creates_new_workspace_when_select_fails(self):
        service = TerraformService()
        call_count = {'count': 0}

        def fake_run(args, cwd=None, capture_output=None, text=None, check=None):
            call_count['count'] += 1
            if 'select' in args:
                raise InfrastructureException('workspace select failed')
            return SimpleNamespace(stdout='')

        with patch.object(BaseInfrastructureService, '_run', side_effect=fake_run):
            service.workspace('/tmp/workspace', 'test')
            self.assertEqual(call_count['count'], 2)


class SSHServiceTests(SimpleTestCase):
    def test_paramiko_ssh_service_can_be_loaded(self):
        fake_paramiko = ModuleType('paramiko')
        class FakeChannel:
            def recv_exit_status(self):
                return 0
        class FakeStdIO:
            def __init__(self):
                self.channel = FakeChannel()
            def read(self):
                return b'ok'
        class FakeSSHClient:
            def __init__(self):
                self.connect = Mock()
                self.open_sftp = Mock(return_value=Mock(put=Mock(), close=Mock()))
            def set_missing_host_key_policy(self, policy):
                self._policy = policy
            def exec_command(self, command, timeout=None, environment=None):
                return (None, FakeStdIO(), FakeStdIO())
            def close(self):
                pass
        def fake_auto_add_policy():
            return object()

        fake_paramiko.SSHClient = FakeSSHClient
        fake_paramiko.AutoAddPolicy = fake_auto_add_policy

        sys.modules['paramiko'] = fake_paramiko
        sys.modules.pop('devops.services.implementations.ssh.base', None)
        sys.modules.pop('devops.services.implementations.ssh.paramiko_ssh_service', None)
        import importlib
        import devops.services.implementations.ssh.base as base_module
        importlib.reload(base_module)
        from devops.services.implementations.ssh.paramiko_ssh_service import ParamikoSSHService
        importlib.reload(__import__('devops.services.implementations.ssh.paramiko_ssh_service', fromlist=['*']))

        service = ParamikoSSHService()
        service.connect('localhost', username='user')
        result = service.execute('echo hello')
        self.assertEqual(result['exit_code'], 0)
        service.copy('/tmp/src', '/tmp/dest')
        service.close()
