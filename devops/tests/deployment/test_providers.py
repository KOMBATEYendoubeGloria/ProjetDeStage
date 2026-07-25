"""Tests for deployment providers and the ProviderRegistry."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from devops.deployment.exceptions import ProviderError
from devops.deployment.providers.base import BaseProvider, ProviderRegistry
from devops.deployment.providers.docker_provider import DockerProvider
from devops.deployment.providers.proxmox_provider import ProxmoxProvider
from devops.deployment.providers.virtualbox_provider import VirtualBoxProvider
from devops.deployment.providers.vmware_provider import VMwareProvider


# ---------------------------------------------------------------------------
# BaseProvider
# ---------------------------------------------------------------------------

class BaseProviderTests(SimpleTestCase):

    def test_cannot_instantiate_abc(self):
        with self.assertRaises(TypeError):
            BaseProvider()


# ---------------------------------------------------------------------------
# ProviderRegistry
# ---------------------------------------------------------------------------

class ProviderRegistryTests(SimpleTestCase):

    def test_register_and_get(self):
        old = ProviderRegistry._registry.copy()
        try:
            ProviderRegistry.register(DockerProvider)
            self.assertIn('docker', ProviderRegistry._registry)
            self.assertIs(ProviderRegistry.get('docker'), DockerProvider)
        finally:
            ProviderRegistry._registry = old

    def test_get_unknown_raises(self):
        with self.assertRaises(ValueError):
            ProviderRegistry.get('nonexistent')

    def test_create_returns_instance(self):
        old = ProviderRegistry._registry.copy()
        try:
            ProviderRegistry.register(DockerProvider)
            instance = ProviderRegistry.create('docker')
            self.assertIsInstance(instance, DockerProvider)
        finally:
            ProviderRegistry._registry = old

    def test_available(self):
        old = ProviderRegistry._registry.copy()
        try:
            ProviderRegistry._registry.clear()
            ProviderRegistry.register(ProxmoxProvider)
            ProviderRegistry.register(DockerProvider)
            names = ProviderRegistry.available()
            self.assertEqual(names, ['docker', 'proxmox'])
        finally:
            ProviderRegistry._registry = old

    def test_register_without_name_raises(self):
        with self.assertRaises(ValueError):
            ProviderRegistry.register(type('BadProvider', (), {}))


# ---------------------------------------------------------------------------
# DockerProvider
# ---------------------------------------------------------------------------

class DockerProviderTests(SimpleTestCase):

    def test_provider_name(self):
        self.assertEqual(DockerProvider.provider_name, 'docker')

    def test_get_required_executors(self):
        self.assertEqual(DockerProvider().get_required_executors(), ['docker'])

    @patch('devops.deployment.providers.docker_provider.DockerExecutor')
    def test_deploy_calls_executor(self, MockExecutor):
        instance = MockExecutor.return_value
        instance.execute.return_value = {'status': 'success'}
        p = DockerProvider()
        result = p.deploy({'name': 'app'}, {'dockerfile': 'FROM alpine'})
        self.assertEqual(result['status'], 'success')
        instance.execute.assert_called_once()

    @patch('devops.deployment.providers.docker_provider.DockerExecutor')
    def test_deploy_wraps_exception(self, MockExecutor):
        instance = MockExecutor.return_value
        instance.execute.side_effect = RuntimeError('boom')
        p = DockerProvider()
        with self.assertRaises(ProviderError):
            p.deploy({'name': 'app'}, {'dockerfile': 'FROM alpine'})

    @patch('devops.deployment.providers.docker_provider.DockerExecutor')
    def test_teardown(self, MockExecutor):
        instance = MockExecutor.return_value
        instance.teardown.return_value = {'status': 'cleaned'}
        p = DockerProvider()
        result = p.teardown({'name': 'app'})
        instance.teardown.assert_called_once()

    def test_status(self):
        result = DockerProvider().status({'name': 'app'})
        self.assertEqual(result['provider'], 'docker')
        self.assertEqual(result['status'], 'active')


# ---------------------------------------------------------------------------
# ProxmoxProvider
# ---------------------------------------------------------------------------

class ProxmoxProviderTests(SimpleTestCase):

    def test_provider_name(self):
        self.assertEqual(ProxmoxProvider.provider_name, 'proxmox')

    def test_get_required_executors(self):
        self.assertEqual(
            ProxmoxProvider().get_required_executors(),
            ['terraform', 'ansible', 'docker'],
        )

    @patch('devops.deployment.providers.proxmox_provider.TerraformExecutor')
    @patch('devops.deployment.providers.proxmox_provider.AnsibleExecutor')
    @patch('devops.deployment.providers.proxmox_provider.DockerExecutor')
    def test_deploy_full_pipeline(self, MockDocker, MockAnsible, MockTF):
        MockTF.return_value.execute.return_value = {'status': 'ok'}
        MockAnsible.return_value.execute.return_value = {'status': 'ok'}
        MockDocker.return_value.execute.return_value = {'status': 'deployed'}
        p = ProxmoxProvider()
        result = p.deploy({'name': 'app'}, {'terraform': '...', 'ansible_playbook': '...', 'dockerfile': '...'})
        self.assertEqual(result['status'], 'deployed')

    @patch('devops.deployment.providers.proxmox_provider.TerraformExecutor')
    def test_provision(self, MockTF):
        MockTF.return_value.execute.return_value = {'vm_ids': [100]}
        result = ProxmoxProvider().provision({'name': 'app'}, {'terraform': '...'})
        self.assertEqual(result['vm_ids'], [100])

    @patch('devops.deployment.providers.proxmox_provider.TerraformExecutor')
    def test_teardown(self, MockTF):
        MockTF.return_value.teardown.return_value = {'status': 'destroyed'}
        result = ProxmoxProvider().teardown({'name': 'app'})
        MockTF.return_value.teardown.assert_called_once()


# ---------------------------------------------------------------------------
# VMwareProvider
# ---------------------------------------------------------------------------

class VMwareProviderTests(SimpleTestCase):

    def test_provider_name(self):
        self.assertEqual(VMwareProvider.provider_name, 'vmware')

    def test_get_required_executors(self):
        self.assertEqual(
            VMwareProvider().get_required_executors(),
            ['terraform', 'ansible', 'docker'],
        )

    @patch('devops.deployment.providers.vmware_provider.TerraformExecutor')
    @patch('devops.deployment.providers.vmware_provider.AnsibleExecutor')
    @patch('devops.deployment.providers.vmware_provider.DockerExecutor')
    def test_deploy_full_pipeline(self, MockDocker, MockAnsible, MockTF):
        MockTF.return_value.execute.return_value = {'status': 'ok'}
        MockAnsible.return_value.execute.return_value = {'status': 'ok'}
        MockDocker.return_value.execute.return_value = {'status': 'deployed'}
        p = VMwareProvider()
        result = p.deploy({'name': 'app'}, {'terraform': '...', 'ansible_playbook': '...', 'dockerfile': '...'})
        self.assertEqual(result['status'], 'deployed')


# ---------------------------------------------------------------------------
# VirtualBoxProvider
# ---------------------------------------------------------------------------

class VirtualBoxProviderTests(SimpleTestCase):

    def test_provider_name(self):
        self.assertEqual(VirtualBoxProvider.provider_name, 'virtualbox')

    def test_get_required_executors(self):
        self.assertEqual(
            VirtualBoxProvider().get_required_executors(),
            ['terraform', 'ansible', 'docker'],
        )

    @patch('devops.deployment.providers.virtualbox_provider.TerraformExecutor')
    @patch('devops.deployment.providers.virtualbox_provider.AnsibleExecutor')
    @patch('devops.deployment.providers.virtualbox_provider.DockerExecutor')
    def test_deploy_full_pipeline(self, MockDocker, MockAnsible, MockTF):
        MockTF.return_value.execute.return_value = {'status': 'ok'}
        MockAnsible.return_value.execute.return_value = {'status': 'ok'}
        MockDocker.return_value.execute.return_value = {'status': 'deployed'}
        p = VirtualBoxProvider()
        result = p.deploy({'name': 'app'}, {'terraform': '...', 'ansible_playbook': '...', 'dockerfile': '...'})
        self.assertEqual(result['status'], 'deployed')
