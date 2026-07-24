from .base import BaseLoggingService


class DefaultLoggingService(BaseLoggingService):
    """Default logging implementation using Python logging."""

    provider_name = 'default'

    def __init__(self) -> None:
        super().__init__()
