from django.test import SimpleTestCase
from devops.exceptions import HypervisorException
from devops.services.implementations.hypervisors.proxmox import ProxmoxService


class HypervisorServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = ProxmoxService()

    def test_vm_lifecycle(self):
        vm_id = self.service.create_vm({'id': 'vm1', 'name': 'test-vm'})
        self.assertEqual(vm_id, 'vm1')
        self.service.start_vm(vm_id)
        self.service.reboot_vm(vm_id)
        self.service.stop_vm(vm_id)
        snapshot_id = self.service.snapshot_vm(vm_id, 'snap1')
        self.assertIn('snap1', snapshot_id)
        self.service.restore_snapshot(vm_id, snapshot_id)
        vms = self.service.list_vms()
        self.assertEqual(len(vms), 1)
        self.service.delete_vm(vm_id)
        with self.assertRaises(HypervisorException):
            self.service.delete_vm(vm_id)
