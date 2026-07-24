"""Default CI/CD Pipeline artifact generator implementation."""

from __future__ import annotations

import logging
from typing import Any, Mapping

from ...interfaces.pipeline_generator import PipelineGeneratorInterface
from ...validators.artifact_validator import ArtifactValidator
from ...engine.template_loader import TemplateLoader
from ...engine.template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)

_CI_TEMPLATE_MAP = {
    'github-actions': 'pipeline/github-actions/{framework}.yml.j2',
    'gitlab-ci': 'pipeline/gitlab-ci/{framework}.yml.j2',
    'jenkins': 'pipeline/jenkins/Jenkinsfile-{framework}.j2',
}

_FALLBACK_CI = {
    'github-actions': 'pipeline/github-actions/generic.yml.j2',
    'gitlab-ci': 'pipeline/gitlab-ci/generic.yml.j2',
    'jenkins': 'pipeline/jenkins/Jenkinsfile-generic.j2',
}


class DefaultPipelineGenerator(PipelineGeneratorInterface):
    """Generate CI/CD pipeline descriptors from a project definition."""

    artifact_type = 'pipeline'

    def __init__(self) -> None:
        self.validator = ArtifactValidator()
        self.loader = TemplateLoader()
        self.renderer = TemplateRenderer()

    def generate(self, project: Mapping[str, Any]) -> str:
        return self.generate_pipeline(project)

    def generate_pipeline(self, project: Mapping[str, Any]) -> str:
        self.validator.validate(project)
        name = project['name']
        ci_platform = project.get('ci_platform', 'github-actions')
        framework = (project.get('framework') or project.get('type') or 'generic').lower()
        logger.info('Generating %s pipeline for %s (%s)', ci_platform, name, framework)

        port = project.get('ports', [8000])[0]
        context = {
            'name': name,
            'framework': framework,
            'version': project.get('version', '3.11'),
            'port': port,
            'docker_image': project.get('docker_image', f'{name}:latest'),
        }

        # Attempt framework-specific template, fall back to generic
        pattern = _CI_TEMPLATE_MAP.get(ci_platform, 'pipeline/github-actions/{framework}.yml.j2')
        fallback = _FALLBACK_CI.get(ci_platform, 'pipeline/github-actions/generic.yml.j2')

        for tpl_name in (pattern.format(framework=framework), fallback):
            try:
                template = self.loader.load(tpl_name)
                return self.renderer.render(template, context)
            except Exception:
                continue

        # Hard fallback: inline minimal pipeline
        logger.warning('All pipeline templates failed for %s, using inline fallback', name)
        return (
            f"# CI/CD Pipeline for {name}\n"
            f"# platform: {ci_platform}\n"
            f"name: deploy-{name}\n"
        )
