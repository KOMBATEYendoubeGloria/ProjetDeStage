"""Tests for RemoteConfig — resolution, validation, serialization."""

from unittest.mock import MagicMock

from django.test import SimpleTestCase

from devops.deployment.exceptions import DeploymentValidationError
from devops.deployment.remote.config import RemoteConfig, _is_remote_config


class IsRemoteConfigTests(SimpleTestCase):

    def test_empty_dict(self):
        self.assertFalse(_is_remote_config({}))

    def test_none(self):
        self.assertFalse(_is_remote_config(None))

    def test_deployment_target_id(self):
        self.assertTrue(_is_remote_config({'deployment_target_id': 1}))

    def test_host_and_ssh_user(self):
        self.assertTrue(_is_remote_config({'host': '10.0.0.1', 'ssh_user': 'root'}))

    def test_host_and_username(self):
        self.assertTrue(_is_remote_config({'host': '10.0.0.1', 'username': 'admin'}))

    def test_host_only_not_remote(self):
        self.assertFalse(_is_remote_config({'host': '10.0.0.1'}))

    def test_ssh_user_only_not_remote(self):
        self.assertFalse(_is_remote_config({'ssh_user': 'root'}))


class RemoteConfigFromConfigTests(SimpleTestCase):

    def test_none_when_not_remote(self):
        result = RemoteConfig.from_config({})
        self.assertIsNone(result)

    def test_none_when_missing_host(self):
        result = RemoteConfig.from_config({'ssh_user': 'root'})
        self.assertIsNone(result)

    def test_none_when_missing_username(self):
        result = RemoteConfig.from_config({'host': '10.0.0.1'})
        self.assertIsNone(result)

    def test_builds_from_explicit_fields(self):
        config = {'host': '10.0.0.1', 'ssh_user': 'root', 'ssh_port': 2222, 'ssh_key': 'key-data'}
        rc = RemoteConfig.from_config(config)
        self.assertIsNotNone(rc)
        self.assertEqual(rc.host, '10.0.0.1')
        self.assertEqual(rc.username, 'root')
        self.assertEqual(rc.port, 2222)
        self.assertEqual(rc.private_key, 'key-data')

    def test_username_alias(self):
        config = {'host': '10.0.0.1', 'username': 'admin'}
        rc = RemoteConfig.from_config(config)
        self.assertIsNotNone(rc)
        self.assertEqual(rc.username, 'admin')

    def test_default_port(self):
        config = {'host': '10.0.0.1', 'ssh_user': 'root'}
        rc = RemoteConfig.from_config(config)
        self.assertEqual(rc.port, 22)

    def test_custom_workspace(self):
        config = {'host': '10.0.0.1', 'ssh_user': 'root', 'remote_workspace': '/opt/deploy'}
        rc = RemoteConfig.from_config(config)
        self.assertEqual(rc.workspace, '/opt/deploy')


class RemoteConfigFromDeploymentTargetTests(SimpleTestCase):

    def test_from_target_with_explicit_credential(self):
        target = MagicMock()
        target.host = '192.168.1.50'
        target.port = 22
        credential = MagicMock()
        credential.username = 'deploy'
        credential.private_key = 'PRIVATE_KEY'
        credential.passphrase = 'secret'
        rc = RemoteConfig.from_deployment_target(target, credential=credential)
        self.assertEqual(rc.host, '192.168.1.50')
        self.assertEqual(rc.username, 'deploy')
        self.assertEqual(rc.private_key, 'PRIVATE_KEY')
        self.assertEqual(rc.passphrase, 'secret')

    def test_from_target_resolves_vm_credential(self):
        vm = MagicMock()
        vm.ssh_credential = MagicMock()
        vm.ssh_credential.username = 'vm_user'
        vm.ssh_credential.private_key = 'VM_KEY'
        vm.ssh_credential.passphrase = ''
        target = MagicMock()
        target.host = '10.0.0.5'
        target.port = 22
        target.virtual_machine = vm
        rc = RemoteConfig.from_deployment_target(target)
        self.assertEqual(rc.host, '10.0.0.5')
        self.assertEqual(rc.username, 'vm_user')
        self.assertEqual(rc.private_key, 'VM_KEY')

    def test_from_target_no_credential(self):
        target = MagicMock()
        target.host = '10.0.0.1'
        target.port = 22
        target.virtual_machine = None
        rc = RemoteConfig.from_deployment_target(target)
        self.assertEqual(rc.host, '10.0.0.1')
        self.assertEqual(rc.username, '')
        self.assertEqual(rc.private_key, '')


class RemoteConfigValidationTests(SimpleTestCase):

    def test_is_remote_true(self):
        rc = RemoteConfig(host='10.0.0.1', username='root')
        self.assertTrue(rc.is_remote())

    def test_is_remote_false_no_host(self):
        rc = RemoteConfig(username='root')
        self.assertFalse(rc.is_remote())

    def test_is_remote_false_no_username(self):
        rc = RemoteConfig(host='10.0.0.1')
        self.assertFalse(rc.is_remote())

    def test_validate_passes(self):
        rc = RemoteConfig(host='10.0.0.1', username='root')
        rc.validate()

    def test_validate_missing_host(self):
        rc = RemoteConfig(username='root')
        with self.assertRaises(DeploymentValidationError):
            rc.validate()

    def test_validate_missing_username(self):
        rc = RemoteConfig(host='10.0.0.1')
        with self.assertRaises(DeploymentValidationError):
            rc.validate()


class RemoteConfigSerializationTests(SimpleTestCase):

    def test_to_dict(self):
        rc = RemoteConfig(host='10.0.0.1', port=2222, username='root', private_key='KEY', password='pass')
        d = rc.to_dict()
        self.assertEqual(d['host'], '10.0.0.1')
        self.assertEqual(d['port'], 2222)
        self.assertEqual(d['username'], 'root')
        self.assertTrue(d['has_private_key'])
        self.assertTrue(d['has_password'])

    def test_to_dict_no_sensitive_data(self):
        rc = RemoteConfig(host='10.0.0.1', username='root', private_key='SECRET')
        d = rc.to_dict()
        self.assertNotIn('private_key', d)
        self.assertNotIn('secret', str(d))

    def test_to_dict_defaults(self):
        rc = RemoteConfig()
        d = rc.to_dict()
        self.assertFalse(d['has_private_key'])
        self.assertFalse(d['has_password'])
