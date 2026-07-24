import logging
from typing import Any, Dict, Optional

from ....exceptions import ConfigurationException
from ...interfaces.configuration import ConfigurationInterface


class BaseConfigurationService(ConfigurationInterface):
    """Base configuration service implementation."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._config: Dict[str, Any] = {}

    def get_configuration(self, key: str) -> Any:
        try:
            value = self._config[key]
        except KeyError as exc:
            self.logger.error('Configuration key not found: %s', key)
            raise ConfigurationException(f'Configuration key not found: {key}') from exc
        self.logger.info('Retrieved configuration key %s', key)
        return value

    def set_configuration(self, key: str, value: Any) -> None:
        self._config[key] = value
        self.logger.info('Stored configuration key %s', key)

    def validate_configuration(self, config_data: Dict[str, Any]) -> None:
        if not isinstance(config_data, dict):
            raise ConfigurationException('Configuration data must be a dict')
        self.logger.info('Validated configuration data with %d keys', len(config_data))
