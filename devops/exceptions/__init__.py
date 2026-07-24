"""Custom exceptions for the DevOps engine."""


class DevopsException(Exception):
    """Base exception for DevOps-related failures."""
    pass


DevOpsException = DevopsException


class GitException(DevopsException):
    """Errors raised during Git operations."""
    pass


class InfrastructureException(DevopsException):
    """Errors raised during infrastructure management."""
    pass


class ContainerException(DevopsException):
    """Errors raised during container management."""
    pass


class SSHException(DevopsException):
    """Errors raised during SSH operations."""
    pass


class HypervisorException(DevopsException):
    """Errors raised during hypervisor management."""
    pass


class DeploymentException(DevopsException):
    """Errors raised during deployment orchestration."""
    pass


class PipelineException(DevopsException):
    """Errors raised during pipeline management."""
    pass


class ValidationException(DevopsException):
    """Errors raised during validation."""
    pass


class ConfigurationException(DevopsException):
    """Errors raised during configuration management."""
    pass
