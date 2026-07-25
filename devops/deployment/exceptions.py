"""Domain exceptions for the deployment engine."""

from __future__ import annotations


class DeploymentEngineError(Exception):
    """Base exception for all deployment engine errors."""

    pass


class ProviderError(DeploymentEngineError):
    """Raised when a deployment provider operation fails."""

    pass


class ExecutorError(DeploymentEngineError):
    """Raised when an executor (Terraform, Ansible, Docker) operation fails."""

    pass


class TerraformExecutorError(ExecutorError):
    """Raised when a Terraform command fails."""

    pass


class AnsibleExecutorError(ExecutorError):
    """Raised when an Ansible command fails."""

    pass


class DockerExecutorError(ExecutorError):
    """Raised when a Docker command fails."""

    pass


class ProviderRegistryError(DeploymentEngineError):
    """Raised when provider lookup or registration fails."""

    pass


class DeploymentValidationError(DeploymentEngineError):
    """Raised when deployment input validation fails."""

    pass


class RollbackError(DeploymentEngineError):
    """Raised when rollback itself fails."""

    pass
