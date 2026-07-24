"""Runtime dependency container for the DevOps service layer."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

from ..interfaces.base import ServiceInterface
from ..factory import ServiceFactory


class ServiceContainerException(Exception):
    """Error raised when the service container cannot resolve dependencies."""


class ServiceContainer:
    """Simple service container that resolves provider-backed dependencies."""

    def __init__(self, defaults: Optional[Dict[Type[ServiceInterface], Dict[str, Any]]] = None) -> None:
        self._defaults: Dict[Type[ServiceInterface], Dict[str, Any]] = defaults or {}
        self._instances: Dict[Type[ServiceInterface], ServiceInterface] = {}

    def resolve(
        self,
        interface: Type[ServiceInterface],
        provider_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> ServiceInterface:
        if (interface, provider_name) in self._instances:
            return self._instances[(interface, provider_name)]

        service_config: Dict[str, Any] = {}
        if config:
            service_config.update(config)
        service_config.update(self._defaults.get(interface, {}))
        try:
            instance = ServiceFactory.create(interface, provider_name=provider_name, config=service_config, **kwargs)
        except Exception as exc:
            raise ServiceContainerException(
                f'Failed to resolve service for {interface.__name__} ({provider_name or "default"}): {exc}'
            ) from exc

        self._instances[(interface, provider_name)] = instance
        return instance

    def set_default_config(self, interface: Type[ServiceInterface], config: Dict[str, Any]) -> None:
        self._defaults[interface] = config

    def clear_cache(self) -> None:
        self._instances.clear()
