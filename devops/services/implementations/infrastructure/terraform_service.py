from .base import BaseInfrastructureService


class TerraformService(BaseInfrastructureService):
    """Terraform implementation."""

    provider_name = 'terraform'

    def __init__(self) -> None:
        super().__init__(binary='terraform')
