from abc import abstractmethod
from typing import Any, Dict, List

from .base import ServiceInterface
from ...exceptions import HypervisorException


class HypervisorInterface(ServiceInterface):
    """Abstract contract for hypervisor management.

    Responsibilities:
        - Manage virtual machine lifecycle across hypervisor providers.
    Excluded responsibilities:
        - Provider-specific hypervisor implementation details.
    """

    @abstractmethod
    def create_vm(self, spec: Dict[str, Any]) -> str:
        """Create a VM and return its identifier."""
        raise HypervisorException('create_vm not implemented')

    @abstractmethod
    def delete_vm(self, vm_id: str) -> None:
        """Delete a virtual machine."""
        raise HypervisorException('delete_vm not implemented')

    @abstractmethod
    def start_vm(self, vm_id: str) -> None:
        """Start a virtual machine."""
        raise HypervisorException('start_vm not implemented')

    @abstractmethod
    def stop_vm(self, vm_id: str) -> None:
        """Stop a virtual machine."""
        raise HypervisorException('stop_vm not implemented')

    @abstractmethod
    def reboot_vm(self, vm_id: str) -> None:
        """Reboot a virtual machine."""
        raise HypervisorException('reboot_vm not implemented')

    @abstractmethod
    def snapshot_vm(self, vm_id: str, name: str) -> str:
        """Create a VM snapshot and return its identifier."""
        raise HypervisorException('snapshot_vm not implemented')

    @abstractmethod
    def restore_snapshot(self, vm_id: str, snapshot_id: str) -> None:
        """Restore a VM from a snapshot."""
        raise HypervisorException('restore_snapshot not implemented')

    @abstractmethod
    def list_vms(self) -> List[Dict[str, Any]]:
        """List VMs managed by the hypervisor."""
        raise HypervisorException('list_vms not implemented')
