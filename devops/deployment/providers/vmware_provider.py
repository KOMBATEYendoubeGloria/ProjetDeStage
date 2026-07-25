"""VMware provider — provisions VMs on vSphere and deploys via SSH."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..executors import AnsibleExecutor, DockerExecutor, TerraformExecutor
from ..exceptions import ProviderError
from .base import BaseProvider

logger = logging.getLogger(__name__)


class VMwareProvider(BaseProvider):
    """Deploy applications on VMware vSphere virtual machines.

    Full pipeline: Terraform provisions VMs via the vsphere provider,
    Ansible configures them, Docker deploys containers.
    """

    provider_name = 'vmware'
    display_name = 'VMware vSphere'

    def get_required_executors(self):
        return ['terraform', 'ansible', 'docker']

    def provision(self, project, artifacts, config=None):
        logger.info('VMware provider: provisioning VMs')
        executor = TerraformExecutor()
        workspace = config.get('workspace', '/tmp/deploy/vmware') if config else '/tmp/deploy/vmware'
        try:
            return executor.execute(workspace, artifacts, config.get('variables') if config else None)
        except Exception as exc:
            raise ProviderError(f'VMware provisioning failed: {exc}') from exc

    def deploy(self, project, artifacts, config=None):
        logger.info('VMware provider: configuring and deploying')
        workspace = config.get('workspace', '/tmp/deploy/vmware') if config else '/tmp/deploy/vmware'
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
            raise ProviderError(f'VMware Docker deployment failed: {exc}') from exc

    def teardown(self, project, config=None):
        logger.info('VMware provider: destroying VMs')
        terraform = TerraformExecutor()
        workspace = config.get('workspace', '/tmp/deploy/vmware') if config else '/tmp/deploy/vmware'
        try:
            return terraform.teardown(workspace, config.get('variables') if config else None)
        except Exception as exc:
            raise ProviderError(f'VMware teardown failed: {exc}') from exc

    def status(self, project, config=None):
        return {'provider': self.provider_name, 'status': 'active'}
