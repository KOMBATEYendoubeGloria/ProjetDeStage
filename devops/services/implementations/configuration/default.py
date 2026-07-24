from .base import BaseConfigurationService


class DefaultConfigurationService(BaseConfigurationService):
    """Default configuration management implementation."""

    provider_name = 'default'

    def __init__(self) -> None:
        super().__init__()
