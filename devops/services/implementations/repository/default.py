from .base import BaseRepositoryService


class DefaultRepositoryService(BaseRepositoryService):
    """Default repository metadata service implementation."""

    provider_name = 'default'

    def __init__(self) -> None:
        super().__init__()
