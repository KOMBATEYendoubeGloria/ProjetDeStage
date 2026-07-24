"""Centralized secret management through the configuration engine."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ...exceptions import ConfigurationException
from ..manager.configuration_manager import ConfigurationManager

logger = logging.getLogger(__name__)


class SecretManager:
    """Resolve and manage secrets stored in central configuration."""

    def __init__(self, configuration_manager: ConfigurationManager) -> None:
        self._configuration_manager = configuration_manager

    def _get_secret_store(self) -> Dict[str, Any]:
        try:
            secrets = self._configuration_manager.get_configuration('secrets')
        except ConfigurationException:
            secrets = {}
            self._configuration_manager.set_configuration('secrets', secrets)

        if not isinstance(secrets, dict):
            raise ConfigurationException('Secrets configuration must be a mapping')

        return secrets

    def list_secrets(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        secrets = self._get_secret_store()
        result = [value for value in secrets.values() if isinstance(value, dict)]
        if project_id:
            result = [secret for secret in result if secret.get('project_id') == project_id]
        logger.info('Listed %d secrets', len(result))
        return result

    def retrieve_secret(self, secret_name: str, environment: Optional[str] = None) -> Dict[str, Any]:
        secrets = self._get_secret_store()
        secret = secrets.get(secret_name)
        if secret is None:
            logger.error('Secret not found: %s', secret_name)
            raise ConfigurationException(f'Secret not found: {secret_name}')

        if environment:
            environment_config = self._configuration_manager.get_environment_configuration(environment)
            overrides = environment_config.get('secrets', {}).get(secret_name, {})
            if isinstance(overrides, dict):
                merged = {**secret, **overrides}
                logger.info('Resolved secret %s with environment overrides for %s', secret_name, environment)
                return merged

        logger.info('Retrieved secret %s', secret_name)
        return secret

    def store_secret(self, secret_name: str, secret_data: Dict[str, Any]) -> None:
        if not isinstance(secret_data, dict):
            raise ConfigurationException('Secret data must be a dict')

        secrets = self._get_secret_store()
        secrets[secret_name] = secret_data
        self._configuration_manager.set_configuration('secrets', secrets)
        logger.info('Stored secret %s', secret_name)
