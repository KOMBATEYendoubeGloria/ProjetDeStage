"""Tests for top-level package imports and exports."""

from django.test import SimpleTestCase

from devops.deployment import (
    AnsibleExecutorError,
    BaseProvider,
    DeploymentEngineError,
    DeploymentOrchestrator,
    DeploymentResult,
    DeploymentService,
    DeploymentValidationError,
    DockerProvider,
    DockerExecutorError,
    ExecutorError,
    ProviderError,
    ProviderRegistry,
    ProviderRegistryError,
    ProxmoxProvider,
    RollbackError,
    TerraformExecutorError,
    VirtualBoxProvider,
    VMwareProvider,
)


class PackageExportTests(SimpleTestCase):

    def test_all_exports_exist(self):
        exports = [
            DeploymentEngineError, ProviderError, ExecutorError,
            TerraformExecutorError, AnsibleExecutorError, DockerExecutorError,
            ProviderRegistryError, DeploymentValidationError, RollbackError,
            BaseProvider, ProviderRegistry,
            DockerProvider, ProxmoxProvider, VMwareProvider, VirtualBoxProvider,
            DeploymentOrchestrator, DeploymentResult, DeploymentService,
        ]
        for obj in exports:
            self.assertIsNotNone(obj)
