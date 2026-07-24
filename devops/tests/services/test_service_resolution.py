import importlib
import sys
from types import ModuleType
from unittest.mock import patch

from django.test import SimpleTestCase

from devops.services import ProviderRegistry, ServiceContainer, ServiceFactory
from devops.services.interfaces.container import ContainerInterface
from devops.services.interfaces.infrastructure import InfrastructureInterface
from devops.services.interfaces.notification import NotificationInterface
from devops.services.interfaces.ssh import SSHInterface
from devops.services.implementations.notification.email import EmailNotificationService
from devops.services.implementations.container.docker import DockerService


class ServiceResolutionTests(SimpleTestCase):
    def test_provider_registry_discovers_container_and_infrastructure_providers(self):
        container_providers = ProviderRegistry.available_providers(ContainerInterface)
        self.assertIn('docker', container_providers)
        self.assertIn('podman', container_providers)

        infra_providers = ProviderRegistry.available_providers(InfrastructureInterface)
        self.assertIn('terraform', infra_providers)
        self.assertIn('opentofu', infra_providers)

    def test_provider_registry_requires_explicit_provider_when_multiple_available(self):
        with self.assertRaises(Exception):
            ProviderRegistry.get(ContainerInterface)

    def test_service_factory_creates_named_provider(self):
        service = ServiceFactory.create(ContainerInterface, provider_name='docker')
        self.assertIsInstance(service, DockerService)

    def test_service_container_caches_and_applies_default_config(self):
        container = ServiceContainer()
        container.set_default_config(NotificationInterface, {'smtp_host': 'localhost', 'smtp_port': 25})
        service_a = container.resolve(NotificationInterface, provider_name='email')
        service_b = container.resolve(NotificationInterface, provider_name='email')
        self.assertIs(service_a, service_b)
        self.assertIsInstance(service_a, EmailNotificationService)
        self.assertEqual(service_a.smtp_host, 'localhost')

    def test_service_container_can_resolve_ssh_provider(self):
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
                self.connect = lambda *args, **kwargs: None
                self.open_sftp = lambda: None

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

        import devops.services.implementations.ssh.base as base_module
        base_module.paramiko = fake_paramiko
        importlib.reload(base_module)

        import devops.services.implementations.ssh.paramiko_ssh_service as ssh_module
        importlib.reload(ssh_module)

        ProviderRegistry.refresh()
        service = ServiceContainer().resolve(SSHInterface, provider_name='paramiko')
        self.assertEqual(service.__class__.__name__, 'ParamikoSSHService')
        self.assertTrue(hasattr(service, 'connect'))
