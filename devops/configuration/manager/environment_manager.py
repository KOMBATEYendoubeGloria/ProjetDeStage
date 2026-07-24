"""Manager for environment lifecycle and metadata."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from ...exceptions import DevopsException

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """Manage platforms environments such as development, test, staging, production."""

    def __init__(self) -> None:
        self._default_environment = 'development'

    def _get_environment_model(self):
        from ...models import Environment
        return Environment

    def list_environments(self) -> List[str]:
        Environment = self._get_environment_model()
        return [environment.slug for environment in Environment.objects.all()]

    def get_environment(self, slug: str):
        Environment = self._get_environment_model()
        try:
            environment = Environment.objects.get(slug=slug)
        except Environment.DoesNotExist as exc:
            logger.error('Environment not found: %s', slug)
            raise DevopsException(f'Environment not found: {slug}') from exc
        logger.info('Retrieved environment %s', slug)
        return environment

    def get_default_environment(self):
        Environment = self._get_environment_model()
        try:
            return Environment.objects.get(is_default=True)
        except Environment.DoesNotExist as exc:
            logger.warning('No default environment found, falling back to %s', self._default_environment)
            return self.get_environment(self._default_environment)

    def create_environment(self, name: str, slug: str, description: str = '', is_default: bool = False):
        Environment = self._get_environment_model()
        environment = Environment.objects.create(name=name, slug=slug, description=description, is_default=is_default)
        logger.info('Created environment %s', slug)
        return environment

    def update_environment(self, slug: str, data: Dict[str, Any]):
        environment = self.get_environment(slug)
        for key, value in data.items():
            setattr(environment, key, value)
        environment.save()
        logger.info('Updated environment %s', slug)
        return environment

    def delete_environment(self, slug: str) -> None:
        environment = self.get_environment(slug)
        environment.delete()
        logger.info('Deleted environment %s', slug)
