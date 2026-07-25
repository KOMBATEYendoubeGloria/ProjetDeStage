"""Tests for deployment engine exceptions."""

from django.test import SimpleTestCase

from devops.deployment.exceptions import (
    AnsibleExecutorError,
    DeploymentEngineError,
    DeploymentValidationError,
    DockerExecutorError,
    ExecutorError,
    ProviderError,
    ProviderRegistryError,
    RollbackError,
    TerraformExecutorError,
)


class ExceptionHierarchyTests(SimpleTestCase):

    def test_all_inherit_from_deployment_engine_error(self):
        for exc_cls in [
            ProviderError,
            ExecutorError,
            TerraformExecutorError,
            AnsibleExecutorError,
            DockerExecutorError,
            ProviderRegistryError,
            DeploymentValidationError,
            RollbackError,
        ]:
            with self.subTest(exc_cls=exc_cls):
                self.assertTrue(issubclass(exc_cls, DeploymentEngineError))

    def test_executor_subclasses(self):
        self.assertTrue(issubclass(TerraformExecutorError, ExecutorError))
        self.assertTrue(issubclass(AnsibleExecutorError, ExecutorError))
        self.assertTrue(issubclass(DockerExecutorError, ExecutorError))

    def test_exceptions_are_raisable(self):
        with self.assertRaises(ProviderError):
            raise ProviderError('provider failed')
        with self.assertRaises(ExecutorError):
            raise ExecutorError('executor failed')
        with self.assertRaises(DeploymentValidationError):
            raise DeploymentValidationError('validation failed')
        with self.assertRaises(RollbackError):
            raise RollbackError('rollback failed')
