"""Factory abstraction for resolving provider implementations."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

from ..interfaces.base import ServiceInterface
from ..registry import ProviderRegistry


class ServiceFactoryException(Exception):
    """Base exception for service factory failures."""


class ServiceFactory:
    """Factory that builds service implementation instances from provider registrations."""

    @classmethod
    def create(
        cls,
        interface: Type[ServiceInterface],
        provider_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> ServiceInterface:
        implementation = ProviderRegistry.get(interface, provider_name)
        try:
            if config is None:
                config = {}
            return implementation(**config, **kwargs)
        except TypeError as exc:
            raise ServiceFactoryException(
                f'Unable to instantiate {implementation.__name__}: {exc}'
            ) from exc
