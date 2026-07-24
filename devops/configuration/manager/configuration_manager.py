"""Manager for centralized configuration data."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ...exceptions import ConfigurationException
from ..schemas.provider_schema import ProviderSchema
from ..manager.validation_manager import ValidationManager

logger = logging.getLogger(__name__)


class ConfigurationManager:
    """Source of truth for configuration across the DevOps platform."""

    def __init__(self) -> None:
        self._configuration: Dict[str, Any] = {}
        self._provider_settings: Dict[str, Dict[str, Any]] = {}
        self._environment_settings: Dict[str, Dict[str, Any]] = {}
        self._profiles: Dict[str, Dict[str, Any]] = {}
        self.validation = ValidationManager()

    def load_configuration(self, config_data: Dict[str, Any]) -> None:
        self.validation.validate(config_data, schema=None)
        normalized = {
            'providers': {},
            'environments': {},
            'profiles': {},
            **config_data,
        }
        self._configuration = normalized
        logger.info('Loaded central configuration with %d top-level keys', len(normalized))

        self._provider_settings = normalized.get('providers', {})
        self._environment_settings = normalized.get('environments', {})
        self._profiles = normalized.get('profiles', {})

    def get_configuration(self, key: str) -> Any:
        try:
            return self._configuration[key]
        except KeyError as exc:
            logger.error('Configuration key not found: %s', key)
            raise ConfigurationException(f'Configuration key not found: {key}') from exc

    def set_configuration(self, key: str, value: Any) -> None:
        self._configuration[key] = value
        logger.info('Set central configuration key %s', key)

    def get_provider_configuration(self, provider_name: str, environment: Optional[str] = None) -> Dict[str, Any]:
        provider_config = self._provider_settings.get(provider_name, {})
        if environment:
            environment_overrides = self._environment_settings.get(environment, {}).get('providers', {}).get(provider_name, {})
            merged = {**provider_config, **environment_overrides}
            logger.info('Resolved provider configuration for %s in environment %s', provider_name, environment)
            return merged
        logger.info('Resolved provider configuration for %s', provider_name)
        return provider_config

    def get_deployment_profile(self, profile_name: str) -> Dict[str, Any]:
        profile = self._profiles.get(profile_name)
        if profile is None:
            logger.error('Deployment profile not found: %s', profile_name)
            raise ConfigurationException(f'Deployment profile not found: {profile_name}')
        logger.info('Selected deployment profile %s', profile_name)
        return profile

    def get_environment_configuration(self, environment_name: str) -> Dict[str, Any]:
        environment = self._environment_settings.get(environment_name)
        if environment is None:
            logger.error('Environment configuration not found: %s', environment_name)
            raise ConfigurationException(f'Environment configuration not found: {environment_name}') from KeyError(environment_name)
        logger.info('Loaded environment configuration %s', environment_name)
        return environment

    def get_provider_names(self) -> list[str]:
        return list(self._provider_settings.keys())

    def get_environment_names(self) -> list[str]:
        return list(self._environment_settings.keys())

    def get_profile_names(self) -> list[str]:
        return list(self._profiles.keys())
