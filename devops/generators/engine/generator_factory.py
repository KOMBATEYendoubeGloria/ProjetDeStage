"""Factory for artifact generators."""

from __future__ import annotations

from typing import Any, Dict, Type


class GeneratorFactory:
    """Registry of generator implementations keyed by artifact family."""

    _registry: Dict[str, Type[Any]] = {}

    @classmethod
    def register(cls, artifact_type: str, generator_cls: Type[Any]) -> None:
        cls._registry[artifact_type] = generator_cls

    @classmethod
    def create(cls, artifact_type: str) -> Any:
        generator_cls = cls._registry.get(artifact_type)
        if generator_cls is None:
            raise ValueError(f'No generator registered for artifact type: {artifact_type}')
        return generator_cls()

