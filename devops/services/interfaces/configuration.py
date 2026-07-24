from abc import abstractmethod
from typing import Any, Dict

from .base import ServiceInterface
from ...exceptions import DevopsException


class ConfigurationInterface(ServiceInterface):
    """Abstract contract for configuration management.

    Responsibilities:
        - Store and validate configuration data.
    Excluded responsibilities:
        - Concrete persistence strategies.
    """

    @abstractmethod
    def get_configuration(self, key: str) -> Any:
        """Return a configuration value by key."""
        raise DevopsException('get_configuration not implemented')

    @abstractmethod
    def set_configuration(self, key: str, value: Any) -> None:
        """Persist a configuration value."""
        raise DevopsException('set_configuration not implemented')

    @abstractmethod
    def validate_configuration(self, config_data: Dict[str, Any]) -> None:
        """Validate configuration data against rules."""
        raise DevopsException('validate_configuration not implemented')
