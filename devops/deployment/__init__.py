"""Deployment engine — multi-provider deployment orchestration for DevOps projects.

Usage::

    from devops.deployment import DeploymentService

    service = DeploymentService()
    result = service.start_deployment(
        provider_name='docker',
        project={'name': 'my-app'},
        artifacts={'dockerfile': '...', 'docker_compose': '...'},
    )
"""

from .exceptions import (
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
from .orchestrator.deployment_orchestrator import DeploymentOrchestrator
from .providers.base import BaseProvider, ProviderRegistry
from .providers.docker_provider import DockerProvider
from .providers.proxmox_provider import ProxmoxProvider
from .providers.virtualbox_provider import VirtualBoxProvider
from .providers.vmware_provider import VMwareProvider
from .result import DeploymentResult
from .services import DeploymentService

__all__ = [
    'DeploymentEngineError',
    'ProviderError',
    'ExecutorError',
    'TerraformExecutorError',
    'AnsibleExecutorError',
    'DockerExecutorError',
    'ProviderRegistryError',
    'DeploymentValidationError',
    'RollbackError',
    'BaseProvider',
    'ProviderRegistry',
    'DockerProvider',
    'ProxmoxProvider',
    'VMwareProvider',
    'VirtualBoxProvider',
    'DeploymentOrchestrator',
    'DeploymentResult',
    'DeploymentService',
]
