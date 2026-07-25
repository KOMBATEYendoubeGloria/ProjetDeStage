"""Base interface and registry for deployment providers."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """Common contract for all deployment providers.

    A provider encapsulates the strategy for deploying an application
    on a specific infrastructure target (Docker local, Proxmox, VMware, etc.).
    Providers are registered via the ``provider_name`` class attribute
    and discovered by ``ProviderRegistry``.
    """

    provider_name: str = 'base'
    display_name: str = 'Base Provider'

    @abstractmethod
    def provision(self, project: Dict[str, Any], artifacts: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Provision infrastructure for the project."""
        raise NotImplementedError

    @abstractmethod
    def deploy(self, project: Dict[str, Any], artifacts: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Deploy the application onto provisioned infrastructure."""
        raise NotImplementedError

    @abstractmethod
    def teardown(self, project: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Destroy infrastructure and clean up resources."""
        raise NotImplementedError

    @abstractmethod
    def status(self, project: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return the current status of the deployment."""
        raise NotImplementedError

    def get_required_executors(self) -> List[str]:
        """Return the list of executor names required by this provider.

        Override in subclasses to specify provider-specific requirements.
        Default: all three executors.
        """
        return ['terraform', 'ansible', 'docker']

    def validate_config(self, config: Optional[Dict[str, Any]]) -> bool:
        """Validate provider-specific configuration. Returns True if valid."""
        return True


class ProviderRegistry:
    """Auto-discovery registry for deployment providers."""

    _registry: Dict[str, Type[BaseProvider]] = {}

    @classmethod
    def register(cls, provider_cls: Type[BaseProvider]) -> None:
        """Register a provider class using its ``provider_name`` attribute."""
        name = getattr(provider_cls, 'provider_name', None)
        if not name:
            raise ValueError(f'{provider_cls.__name__} has no provider_name attribute')
        cls._registry[name] = provider_cls
        logger.debug('Registered provider: %s -> %s', name, provider_cls.__name__)

    @classmethod
    def get(cls, provider_name: str) -> Type[BaseProvider]:
        """Retrieve a registered provider class by name."""
        provider_cls = cls._registry.get(provider_name)
        if provider_cls is None:
            raise ValueError(f'No provider registered for: {provider_name}')
        return provider_cls

    @classmethod
    def create(cls, provider_name: str, **kwargs: Any) -> BaseProvider:
        """Instantiate a provider by name."""
        return cls.get(provider_name)(**kwargs)

    @classmethod
    def available(cls) -> List[str]:
        """Return all registered provider names."""
        return sorted(cls._registry.keys())
