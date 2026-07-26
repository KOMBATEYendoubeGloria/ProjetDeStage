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
from .remote.command_runner import LocalCommandRunner, SSHCommandRunner
from .remote.config import RemoteConfig
from .result import DeploymentResult
from .services import DeploymentService
from .async_engine import CancellationToken, CancellationError, DeploymentJobManager
from .events import EventBus
from .monitoring import DeploymentMonitor, PersistentDeploymentMonitor
from .progress import StageTracker

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
    'RemoteConfig',
    'LocalCommandRunner',
    'SSHCommandRunner',
    'CancellationToken',
    'CancellationError',
    'DeploymentJobManager',
    'EventBus',
    'DeploymentMonitor',
    'PersistentDeploymentMonitor',
    'StageTracker',
]
