"""Deployment providers package."""

from .base import BaseProvider, ProviderRegistry
from .docker_provider import DockerProvider
from .proxmox_provider import ProxmoxProvider
from .vmware_provider import VMwareProvider
from .virtualbox_provider import VirtualBoxProvider

ProviderRegistry.register(DockerProvider)
ProviderRegistry.register(ProxmoxProvider)
ProviderRegistry.register(VMwareProvider)
ProviderRegistry.register(VirtualBoxProvider)

__all__ = [
    'BaseProvider',
    'ProviderRegistry',
    'DockerProvider',
    'ProxmoxProvider',
    'VMwareProvider',
    'VirtualBoxProvider',
]
