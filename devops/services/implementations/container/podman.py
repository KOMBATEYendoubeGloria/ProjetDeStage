from .base import BaseContainerService


class PodmanService(BaseContainerService):
    """Podman engine implementation."""

    provider_name = 'podman'

    def __init__(self) -> None:
        super().__init__(engine='podman')
