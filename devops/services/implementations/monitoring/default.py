from .base import BaseMonitoringService


class DefaultMonitoringService(BaseMonitoringService):
    """Default monitoring implementation."""

    provider_name = 'default'

    def __init__(self) -> None:
        super().__init__()
