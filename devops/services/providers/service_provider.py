"""Types used by the DevOps service provider registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

from .provider_config import ProviderConfig


@dataclass
class ServiceProvider:
    """Representation of a registered service provider."""

    interface: Type[Any]
    provider_name: str
    implementation: Type[Any]
    module: str
    version: str = '0.0.0'
    description: str = ''
    author: str = ''
    capabilities: List[str] = None
    compatibility: Optional[str] = None
    dependencies: List[str] = None
    config: Dict[str, Any] = None
    active: bool = True
    status: str = 'active'

    def __post_init__(self) -> None:
        self.capabilities = self.capabilities or []
        self.dependencies = self.dependencies or []
        self.config = self.config or {}

    def settings(self) -> Dict[str, Any]:
        return dict(self.config or {})

    def describe(self) -> Dict[str, Any]:
        return {
            'interface': getattr(self.interface, '__name__', str(self.interface)),
            'provider_name': self.provider_name,
            'module': self.module,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'capabilities': list(self.capabilities),
            'compatibility': self.compatibility,
            'dependencies': list(self.dependencies),
            'config': dict(self.config),
            'active': self.active,
            'status': self.status,
        }

    def as_provider_config(self) -> ProviderConfig:
        return ProviderConfig(provider_name=self.provider_name, settings=self.settings(), active=self.active)
