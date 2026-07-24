from .base import BaseHypervisorService


class ProxmoxService(BaseHypervisorService):
    """Proxmox hypervisor implementation."""

    provider_name = 'proxmox'

    def __init__(self) -> None:
        super().__init__()
