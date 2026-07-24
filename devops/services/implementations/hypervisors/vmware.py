from .base import BaseHypervisorService


class VMwareService(BaseHypervisorService):
    """VMware hypervisor implementation."""

    provider_name = 'vmware'

    def __init__(self) -> None:
        super().__init__()
