from .base import BaseDeploymentService


class DefaultDeploymentService(BaseDeploymentService):
    """Default deployment orchestration implementation."""

    provider_name = 'default'

    def __init__(self) -> None:
        super().__init__()
