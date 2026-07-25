"""Proxmox provider — provisions VMs on Proxmox VE and deploys via SSH."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..executors import AnsibleExecutor, DockerExecutor, TerraformExecutor
from ..exceptions import ProviderError
from .base import BaseProvider

logger = logging.getLogger(__name__)


class ProxmoxProvider(BaseProvider):
    """Deploy applications on Proxmox VE virtual machines.

    Full pipeline: Terraform provisions VMs, Ansible configures them,
    Docker deploys containers onto the VMs.
    """

    provider_name = 'proxmox'
    display_name = 'Proxmox VE'

    def get_required_executors(self):
        return ['terraform', 'ansible', 'docker']

    def provision(self, project, artifacts, config=None):
        logger.info('Proxmox provider: provisioning VMs')
        executor = TerraformExecutor()
        workspace = config.get('workspace', '/tmp/deploy/proxmox') if config else '/tmp/deploy/proxmox'
        try:
            return executor.execute(workspace, artifacts, config.get('variables') if config else None)
        except Exception as exc:
            raise ProviderError(f'Proxmox provisioning failed: {exc}') from exc

    def deploy(self, project, artifacts, config=None):
        logger.info('Proxmox provider: configuring and deploying')
        workspace = config.get('workspace', '/tmp/deploy/proxmox') if config else '/tmp/deploy/proxmox'
        variables = config.get('variables') if config else None

        ansible = AnsibleExecutor()
        try:
            ansible.execute(workspace, artifacts, variables)
        except Exception as exc:
            logger.warning('Ansible configuration skipped: %s', exc)

        docker = DockerExecutor()
        try:
            return docker.execute(workspace, artifacts, variables)
        except Exception as exc:
            raise ProviderError(f'Proxmox Docker deployment failed: {exc}') from exc

    def teardown(self, project, config=None):
        logger.info('Proxmox provider: destroying VMs')
        terraform = TerraformExecutor()
        workspace = config.get('workspace', '/tmp/deploy/proxmox') if config else '/tmp/deploy/proxmox'
        try:
            return terraform.teardown(workspace, config.get('variables') if config else None)
        except Exception as exc:
            raise ProviderError(f'Proxmox teardown failed: {exc}') from exc

    def status(self, project, config=None):
        return {'provider': self.provider_name, 'status': 'active'}
