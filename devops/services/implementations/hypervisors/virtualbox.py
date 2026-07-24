from .base import BaseHypervisorService


class VirtualBoxService(BaseHypervisorService):
    """VirtualBox hypervisor implementation."""

    provider_name = 'virtualbox'

    def __init__(self) -> None:
        super().__init__()
