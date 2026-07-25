"""VirtualBox provider — provisions local VMs and deploys via SSH."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..executors import AnsibleExecutor, DockerExecutor, TerraformExecutor
from ..exceptions import ProviderError
from .base import BaseProvider

logger = logging.getLogger(__name__)


class VirtualBoxProvider(BaseProvider):
    """Deploy applications on local VirtualBox virtual machines.

    Full pipeline: Terraform provisions VMs, Ansible configures them,
    Docker deploys containers onto the VMs.
    """

    provider_name = 'virtualbox'
    display_name = 'VirtualBox (Local)'

    def get_required_executors(self):
        return ['terraform', 'ansible', 'docker']

    def provision(self, project, artifacts, config=None):
        logger.info('VirtualBox provider: provisioning VMs')
        executor = TerraformExecutor()
        workspace = config.get('workspace', '/tmp/deploy/virtualbox') if config else '/tmp/deploy/virtualbox'
        try:
            return executor.execute(workspace, artifacts, config.get('variables') if config else None)
        except Exception as exc:
            raise ProviderError(f'VirtualBox provisioning failed: {exc}') from exc

    def deploy(self, project, artifacts, config=None):
        logger.info('VirtualBox provider: configuring and deploying')
        workspace = config.get('workspace', '/tmp/deploy/virtualbox') if config else '/tmp/deploy/virtualbox'
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
            raise ProviderError(f'VirtualBox Docker deployment failed: {exc}') from exc

    def teardown(self, project, config=None):
        logger.info('VirtualBox provider: destroying VMs')
        terraform = TerraformExecutor()
        workspace = config.get('workspace', '/tmp/deploy/virtualbox') if config else '/tmp/deploy/virtualbox'
        try:
            return terraform.teardown(workspace, config.get('variables') if config else None)
        except Exception as exc:
            raise ProviderError(f'VirtualBox teardown failed: {exc}') from exc

    def status(self, project, config=None):
        return {'provider': self.provider_name, 'status': 'active'}
