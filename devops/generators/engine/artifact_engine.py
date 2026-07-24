"""Central ArtifactEngine — orchestrates all DevOps artifact generators."""

from __future__ import annotations

import logging
from typing import Any, Mapping

from .generated_artifacts import GeneratedArtifacts
from .generator_factory import GeneratorFactory
from ..implementations.docker.default import DefaultDockerGenerator
from ..implementations.environment.default import DefaultEnvironmentGenerator
from ..implementations.terraform.default import DefaultTerraformGenerator
from ..implementations.ansible.default import DefaultAnsibleGenerator
from ..implementations.pipeline.default import DefaultPipelineGenerator
from ..analyzer.project_analyzer import ProjectAnalyzer

logger = logging.getLogger(__name__)

# Register concrete implementations (idempotent on re-import)
GeneratorFactory.register('docker', DefaultDockerGenerator)
GeneratorFactory.register('environment', DefaultEnvironmentGenerator)
GeneratorFactory.register('terraform', DefaultTerraformGenerator)
GeneratorFactory.register('ansible', DefaultAnsibleGenerator)
GeneratorFactory.register('pipeline', DefaultPipelineGenerator)


class ArtifactEngine:
    """Central engine for DevOps artifact generation.

    Usage::

        engine = ArtifactEngine()
        artifacts = engine.generate_all(project)
    """

    def __init__(self) -> None:
        self._analyzer = ProjectAnalyzer()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _enrich(self, project: Mapping[str, Any]) -> dict:
        return self._analyzer.enrich_project_metadata(dict(project))

    def _record_history(self, project: dict, artifacts: GeneratedArtifacts, status: str = 'SUCCESS') -> None:  # noqa: E501
        """Persist generation run to GenerationHistory (DB-safe, no secrets)."""
        try:
            from devops.models import GenerationHistory  # local import to avoid circular deps
            GenerationHistory.objects.create(
                project_name=project.get('name', 'unknown'),
                framework=project.get('framework', ''),
                provider=project.get('provider', ''),
                ci_platform=project.get('ci_platform', ''),
                artifacts_generated={
                    k: bool(v) for k, v in artifacts.to_dict().items()
                    if k != 'metadata'
                },
                status=status,
            )
        except Exception as exc:
            logger.warning('Could not record GenerationHistory: %s', exc)

    # ------------------------------------------------------------------
    # Individual generators
    # ------------------------------------------------------------------
    def generate_dockerfile(self, project: Mapping[str, Any]) -> str:
        enriched = self._enrich(project)
        generator = GeneratorFactory.create('docker')
        return generator.generate_dockerfile(enriched)

    def generate_docker_compose(self, project: Mapping[str, Any]) -> str:
        enriched = self._enrich(project)
        generator = GeneratorFactory.create('docker')
        return generator.generate_docker_compose(enriched)

    def generate_environment(self, project: Mapping[str, Any]) -> str:
        enriched = self._enrich(project)
        generator = GeneratorFactory.create('environment')
        return generator.generate_environment(enriched)

    def generate_terraform(self, project: Mapping[str, Any]) -> str:
        enriched = self._enrich(project)
        generator = GeneratorFactory.create('terraform')
        return generator.generate_terraform(enriched)

    def generate_ansible(self, project: Mapping[str, Any]) -> str:
        enriched = self._enrich(project)
        generator = GeneratorFactory.create('ansible')
        return generator.generate_ansible(enriched)

    def generate_pipeline(self, project: Mapping[str, Any]) -> str:
        enriched = self._enrich(project)
        generator = GeneratorFactory.create('pipeline')
        return generator.generate_pipeline(enriched)

    # ------------------------------------------------------------------
    # generate_all — returns structured GeneratedArtifacts
    # ------------------------------------------------------------------
    def generate_all(self, project: Mapping[str, Any], record_history: bool = True) -> GeneratedArtifacts:
        """Generate all DevOps artifacts and return a GeneratedArtifacts object."""
        enriched = self._enrich(project)
        logger.info('ArtifactEngine: generating all artifacts for %s', enriched.get('name'))

        status = 'SUCCESS'
        try:
            artifacts = GeneratedArtifacts(
                dockerfile=self.generate_dockerfile(enriched),
                docker_compose=self.generate_docker_compose(enriched),
                environment=self.generate_environment(enriched),
                terraform=self.generate_terraform(enriched),
                ansible_playbook=self.generate_ansible(enriched),
                ansible_inventory=GeneratorFactory.create('ansible').generate_inventory(enriched),
                pipeline=self.generate_pipeline(enriched),
                metadata={
                    'project_name': enriched.get('name'),
                    'framework': enriched.get('framework'),
                    'provider': enriched.get('provider'),
                    'ci_platform': enriched.get('ci_platform'),
                    'environment': enriched.get('environment'),
                },
            )
        except Exception as exc:
            logger.error('ArtifactEngine generation failed: %s', exc)
            status = 'FAILED'
            raise
        finally:
            if record_history:
                try:
                    self._record_history(enriched, GeneratedArtifacts() if status == 'FAILED' else artifacts, status)
                except Exception:
                    pass

        return artifacts
