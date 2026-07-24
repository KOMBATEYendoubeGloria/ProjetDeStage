"""Manager for provider-specific configuration retrieval."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ...exceptions import ConfigurationException
from ..schemas.provider_schema import ProviderSchema
from .configuration_manager import ConfigurationManager
from .validation_manager import ValidationManager

logger = logging.getLogger(__name__)


class ProviderConfigurationManager:
    """Access provider settings through the centralized configuration engine."""

    def __init__(self, configuration_manager: ConfigurationManager) -> None:
        self._configuration_manager = configuration_manager

    def get_provider_configuration(self, provider_name: str, environment: Optional[str] = None) -> Dict[str, Any]:
        try:
            return self._configuration_manager.get_provider_configuration(provider_name, environment=environment)
        except Exception as exc:
            logger.error('Failed to resolve provider configuration for %s: %s', provider_name, exc)
            raise ConfigurationException(f'Provider configuration unavailable: {provider_name}') from exc

    def validate_provider_configuration(self, provider_name: str, config_data: Dict[str, Any]) -> None:
        schema = ProviderSchema.get_schema(provider_name)
        if schema is None:
            logger.warning('No schema found for provider %s, skipping validation', provider_name)
            return
        ValidationManager().validate(config_data, schema=schema)
        logger.info('Validated provider configuration for %s', provider_name)
