from django.test import SimpleTestCase
from devops.exceptions import ConfigurationException, DevopsException
from devops.services.implementations.artifact.default import DefaultArtifactService
from devops.services.implementations.configuration.default import DefaultConfigurationService
from devops.services.implementations.environment.default import DefaultEnvironmentService
from devops.services.implementations.repository.default import DefaultRepositoryService
from devops.services.implementations.secret.default import DefaultSecretService


class ConfigurationServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = DefaultConfigurationService()

    def test_set_and_get_configuration(self):
        self.service.set_configuration('key', 'value')
        self.assertEqual(self.service.get_configuration('key'), 'value')

    def test_get_configuration_raises_for_missing_key(self):
        with self.assertRaises(ConfigurationException):
            self.service.get_configuration('missing')


class RepositoryServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = DefaultRepositoryService()

    def test_add_get_list_remove_repository(self):
        repo_id = self.service.add_repository({'id': 'repo1', 'name': 'repo1'})
        self.assertEqual(repo_id, 'repo1')
        repo = self.service.get_repository(repo_id)
        self.assertEqual(repo['name'], 'repo1')
        self.assertEqual(len(self.service.list_repositories()), 1)
        self.service.remove_repository(repo_id)
        with self.assertRaises(DevopsException):
            self.service.get_repository(repo_id)


class ArtifactServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = DefaultArtifactService()

    def test_store_retrieve_list_delete_artifact(self):
        artifact_id = self.service.store_artifact({'id': 'artifact1', 'project_id': 'p1'}, payload={'data': 1})
        self.assertEqual(artifact_id, 'artifact1')
        artifact = self.service.retrieve_artifact(artifact_id)
        self.assertEqual(artifact['metadata']['project_id'], 'p1')
        self.assertEqual(len(self.service.list_artifacts(project_id='p1')), 1)
        self.service.delete_artifact(artifact_id)
        with self.assertRaises(DevopsException):
            self.service.retrieve_artifact(artifact_id)


class EnvironmentServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = DefaultEnvironmentService()

    def test_create_get_update_delete_environment(self):
        env_id = self.service.create_environment({'id': 'env1', 'name': 'dev'})
        self.assertEqual(env_id, 'env1')
        self.service.update_environment(env_id, {'name': 'dev2'})
        environment = self.service.get_environment(env_id)
        self.assertEqual(environment['name'], 'dev2')
        self.assertEqual(len(self.service.list_environments()), 1)
        self.service.delete_environment(env_id)
        with self.assertRaises(DevopsException):
            self.service.get_environment(env_id)


class SecretServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = DefaultSecretService()

    def test_store_retrieve_list_delete_secret(self):
        secret_id = self.service.store_secret({'id': 'secret1', 'project_id': 'p1', 'value': 'hidden'})
        self.assertEqual(secret_id, 'secret1')
        secret = self.service.retrieve_secret(secret_id)
        self.assertEqual(secret['project_id'], 'p1')
        self.assertEqual(len(self.service.list_secrets(project_id='p1')), 1)
        self.service.delete_secret(secret_id)
        with self.assertRaises(DevopsException):
            self.service.retrieve_secret(secret_id)
