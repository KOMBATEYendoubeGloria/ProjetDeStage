"""Default Environment artifact generator implementation."""

from __future__ import annotations

import logging
from typing import Any, Mapping

from ...interfaces.environment_generator import EnvironmentGeneratorInterface
from ...validators.artifact_validator import ArtifactValidator
from ...engine.template_loader import TemplateLoader
from ...engine.template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class DefaultEnvironmentGenerator(EnvironmentGeneratorInterface):
    """Generate .env file content from a project definition."""

    artifact_type = 'environment'

    def __init__(self) -> None:
        self.validator = ArtifactValidator()
        self.loader = TemplateLoader()
        self.renderer = TemplateRenderer()

    def generate(self, project: Mapping[str, Any]) -> str:
        return self.generate_environment(project)

    def generate_environment(self, project: Mapping[str, Any]) -> str:
        self.validator.validate(project)
        name = project['name']
        logger.info('Generating .env for %s', name)
        port = project.get('ports', [8000])[0]
        context = {
            'name': name,
            'environment': project.get('environment', 'dev'),
            'port': port,
            'database_name': project.get('database_name', name.replace('-', '_') + '_db'),
            'database_user': project.get('database_user', name.replace('-', '_') + '_user'),
            'database_password': project.get('database_password', 'changeme'),
            'secret_key': project.get('secret_key', 'change-me-in-production'),
        }
        try:
            template = self.loader.load('environment/env.j2')
            return self.renderer.render(template, context)
        except Exception:
            logger.warning('Template not found, using fallback for environment')
            lines = [f"{k.upper()}={v}" for k, v in context.items()]
            return '\n'.join(lines) + '\n'
