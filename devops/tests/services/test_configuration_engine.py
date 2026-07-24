from django.test import SimpleTestCase

from devops.configuration.manager.configuration_manager import ConfigurationManager
from devops.configuration.manager.provider_configuration_manager import ProviderConfigurationManager
from devops.configuration.manager.validation_manager import ValidationManager
from devops.configuration.schemas.provider_schema import ProviderSchema
from devops.configuration.secrets.secret_manager import SecretManager
from devops.configuration.profiles.deployment_profile import DeploymentProfileManager
from devops.exceptions import ConfigurationException, ValidationException


class ConfigurationManagerTests(SimpleTestCase):
    def setUp(self):
        self.manager = ConfigurationManager()
        self.sample_config = {
            'providers': {
                'email': {
                    'smtp_host': 'smtp.example.com',
                    'smtp_port': 587,
                }
            },
            'environments': {
                'production': {
                    'providers': {
                        'email': {
                            'smtp_port': 465,
                        }
                    }
                }
            },
            'profiles': {
                'fast-deploy': {
                    'timeout': 30,
                }
            },
        }

    def test_load_and_retrieve_provider_configuration(self):
        self.manager.load_configuration(self.sample_config)
        config = self.manager.get_provider_configuration('email')
        self.assertEqual(config['smtp_host'], 'smtp.example.com')
        self.assertEqual(config['smtp_port'], 587)

    def test_get_provider_configuration_with_environment_overrides(self):
        self.manager.load_configuration(self.sample_config)
        config = self.manager.get_provider_configuration('email', environment='production')
        self.assertEqual(config['smtp_host'], 'smtp.example.com')
        self.assertEqual(config['smtp_port'], 465)

    def test_get_environment_configuration_missing_raises(self):
        self.manager.load_configuration(self.sample_config)
        with self.assertRaises(ConfigurationException):
            self.manager.get_environment_configuration('nonexistent')

    def test_get_deployment_profile(self):
        self.manager.load_configuration(self.sample_config)
        profile = self.manager.get_deployment_profile('fast-deploy')
        self.assertEqual(profile['timeout'], 30)

    def test_load_configuration_can_accept_empty_schema(self):
        self.manager.load_configuration({})
        self.assertEqual(self.manager.get_configuration('providers'), {})


class ProviderSchemaTests(SimpleTestCase):
    def test_register_and_retrieve_schema(self):
        schema = {
            'type': 'object',
            'properties': {
                'smtp_host': {'type': 'string'},
                'smtp_port': {'type': 'integer'},
            },
            'required': ['smtp_host'],
        }
        ProviderSchema.register_schema('email', schema)
        self.assertEqual(ProviderSchema.get_schema('email'), schema)
        self.assertIn('email', ProviderSchema.available_schemas())


class ProviderConfigurationManagerTests(SimpleTestCase):
    def setUp(self):
        self.configuration_manager = ConfigurationManager()
        self.configuration_manager.load_configuration({'providers': {'email': {'smtp_host': 'smtp.example.com'}}})
        self.provider_manager = ProviderConfigurationManager(self.configuration_manager)

    def test_get_provider_configuration(self):
        config = self.provider_manager.get_provider_configuration('email')
        self.assertEqual(config['smtp_host'], 'smtp.example.com')

    def test_validate_provider_configuration_raises_for_invalid(self):
        schema = {
            'type': 'object',
            'properties': {
                'smtp_host': {'type': 'string'},
                'smtp_port': {'type': 'integer'},
            },
            'required': ['smtp_host', 'smtp_port'],
        }
        ProviderSchema.register_schema('email', schema)
        with self.assertRaises(ValidationException):
            self.provider_manager.validate_provider_configuration('email', {'smtp_host': 'smtp.example.com'})


class SecretManagerTests(SimpleTestCase):
    def setUp(self):
        self.configuration_manager = ConfigurationManager()
        self.secret_manager = SecretManager(self.configuration_manager)

    def test_store_and_retrieve_secret(self):
        self.secret_manager.store_secret('api_token', {'value': 'secret', 'project_id': 'p1'})
        secret = self.secret_manager.retrieve_secret('api_token')
        self.assertEqual(secret['value'], 'secret')
        self.assertEqual(len(self.secret_manager.list_secrets()), 1)

    def test_retrieve_secret_missing_raises(self):
        with self.assertRaises(ConfigurationException):
            self.secret_manager.retrieve_secret('missing')


class DeploymentProfileManagerTests(SimpleTestCase):
    def setUp(self):
        self.configuration_manager = ConfigurationManager()
        self.configuration_manager.load_configuration({'profiles': {'fast-deploy': {'timeout': 30}}})
        self.profile_manager = DeploymentProfileManager(self.configuration_manager)

    def test_apply_profile_merges_configuration(self):
        merged = self.profile_manager.apply_profile('fast-deploy', {'timeout': 60, 'keep_alive': True})
        self.assertEqual(merged['timeout'], 30)
        self.assertTrue(merged['keep_alive'])
