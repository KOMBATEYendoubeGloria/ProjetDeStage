from typing import Dict, Type
from .base import BaseService


class ServiceRegistry:
    """Registry for DevOps service classes."""

    _registry: Dict[str, Type[BaseService]] = {}

    @classmethod
    def register(cls, name: str, service: Type[BaseService]):
        cls._registry[name] = service

    @classmethod
    def get(cls, name: str) -> Type[BaseService]:
        return cls._registry[name]
