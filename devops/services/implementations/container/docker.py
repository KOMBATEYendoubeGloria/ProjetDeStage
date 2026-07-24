from .base import BaseContainerService


class DockerService(BaseContainerService):
    """Docker engine implementation."""

    provider_name = 'docker'

    def __init__(self) -> None:
        super().__init__(engine='docker')
