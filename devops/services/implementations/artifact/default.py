from .base import BaseArtifactService


class DefaultArtifactService(BaseArtifactService):
    """Default artifact storage implementation."""

    provider_name = 'default'

    def __init__(self) -> None:
        super().__init__()
