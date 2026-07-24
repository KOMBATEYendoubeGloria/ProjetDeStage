from .base import BaseSecretService


class DefaultSecretService(BaseSecretService):
    """Default secret management implementation."""
    provider_name = 'default'
    def __init__(self) -> None:
        super().__init__()
