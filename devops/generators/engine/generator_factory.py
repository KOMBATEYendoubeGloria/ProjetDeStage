"""Factory for artifact generators."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Type

from ..interfaces.ansible_generator import AnsibleGeneratorInterface
from ..interfaces.docker_generator import DockerGeneratorInterface
from ..interfaces.environment_generator import EnvironmentGeneratorInterface
from ..interfaces.pipeline_generator import PipelineGeneratorInterface
from ..interfaces.terraform_generator import TerraformGeneratorInterface


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


GeneratorFactory.register('docker', type('DockerGeneratorDefault', (DockerGeneratorInterface,), {}))
GeneratorFactory.register('terraform', type('TerraformGeneratorDefault', (TerraformGeneratorInterface,), {}))
GeneratorFactory.register('ansible', type('AnsibleGeneratorDefault', (AnsibleGeneratorInterface,), {}))
GeneratorFactory.register('pipeline', type('PipelineGeneratorDefault', (PipelineGeneratorInterface,), {}))
GeneratorFactory.register('environment', type('EnvironmentGeneratorDefault', (EnvironmentGeneratorInterface,), {}))
