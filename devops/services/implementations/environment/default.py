from .base import BaseEnvironmentService


class DefaultEnvironmentService(BaseEnvironmentService):
    """Default environment management implementation."""

    provider_name = 'default'

    def __init__(self) -> None:
        super().__init__()
