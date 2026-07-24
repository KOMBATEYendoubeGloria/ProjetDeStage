from .base import BaseInfrastructureService


class OpenTofuService(BaseInfrastructureService):
    """OpenTofu implementation."""

    provider_name = 'opentofu'

    def __init__(self) -> None:
        super().__init__(binary='opentofu')
