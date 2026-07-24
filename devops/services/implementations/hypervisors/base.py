import logging
from typing import Any, Dict, List

from ....exceptions import HypervisorException
from ...interfaces.hypervisor import HypervisorInterface


class BaseHypervisorService(HypervisorInterface):
    """Base hypervisor implementation with provider metadata."""

    provider_name: str = 'base'

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.virtual_machines: Dict[str, Dict[str, Any]] = {}

    def create_vm(self, spec: Dict[str, Any]) -> str:
        vm_id = spec.get('id') or spec.get('name')
        if not vm_id:
            raise HypervisorException('Virtual machine spec requires an id or name')
        self.virtual_machines[vm_id] = {
            'id': vm_id,
            'name': spec.get('name', vm_id),
            'spec': spec,
            'state': 'stopped',
        }
        self.logger.info('Created VM %s on %s', vm_id, self.provider_name)
        return vm_id

    def delete_vm(self, vm_id: str) -> None:
        if vm_id not in self.virtual_machines:
            raise HypervisorException('VM not found')
        del self.virtual_machines[vm_id]
        self.logger.info('Deleted VM %s from %s', vm_id, self.provider_name)

    def start_vm(self, vm_id: str) -> None:
        vm = self.virtual_machines.get(vm_id)
        if not vm:
            raise HypervisorException('VM not found')
        vm['state'] = 'running'
        self.logger.info('Started VM %s on %s', vm_id, self.provider_name)

    def stop_vm(self, vm_id: str) -> None:
        vm = self.virtual_machines.get(vm_id)
        if not vm:
            raise HypervisorException('VM not found')
        vm['state'] = 'stopped'
        self.logger.info('Stopped VM %s on %s', vm_id, self.provider_name)

    def reboot_vm(self, vm_id: str) -> None:
        vm = self.virtual_machines.get(vm_id)
        if not vm:
            raise HypervisorException('VM not found')
        vm['state'] = 'running'
        self.logger.info('Rebooted VM %s on %s', vm_id, self.provider_name)

    def snapshot_vm(self, vm_id: str, name: str) -> str:
        if vm_id not in self.virtual_machines:
            raise HypervisorException('VM not found')
        snapshot_id = f'{vm_id}-{name}'
        self.virtual_machines[vm_id].setdefault('snapshots', []).append(snapshot_id)
        self.logger.info('Snapshot %s created for VM %s on %s', name, vm_id, self.provider_name)
        return snapshot_id

    def restore_snapshot(self, vm_id: str, snapshot_id: str) -> None:
        vm = self.virtual_machines.get(vm_id)
        if not vm or snapshot_id not in vm.get('snapshots', []):
            raise HypervisorException('Snapshot not found')
        vm['state'] = 'running'
        self.logger.info('Restored snapshot %s for VM %s on %s', snapshot_id, vm_id, self.provider_name)

    def list_vms(self) -> List[Dict[str, Any]]:
        self.logger.info('Listing VMs on %s', self.provider_name)
        return list(self.virtual_machines.values())
