"""Proxmox provider — provisions VMs on Proxmox VE and deploys via SSH."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..executors import AnsibleExecutor, DockerExecutor, TerraformExecutor
from ..exceptions import ProviderError
from .base import BaseProvider
from .remote_helpers import (
    close_ssh,
    connect_ssh,
    create_ssh_command_runner,
    get_remote_workspace,
    resolve_remote_config,
    transfer_artifacts_to_remote,
)

logger = logging.getLogger(__name__)


class ProxmoxProvider(BaseProvider):
    """Deploy applications on Proxmox VE virtual machines.

    Full pipeline: Terraform provisions VMs, Ansible configures them,
    Docker deploys containers onto the VMs.

    Supports remote deployment via SSH when config contains host/ssh_user.
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
        remote_config = resolve_remote_config(config)

        if remote_config and remote_config.is_remote():
            return self._deploy_remote(artifacts, config, remote_config)

        return self._deploy_local(artifacts, config)

    def _deploy_local(self, artifacts, config):
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

    def _deploy_remote(self, artifacts, config, remote_config):
        ssh = None
        try:
            ssh = connect_ssh(remote_config)
            remote_workspace = get_remote_workspace(config, 'proxmox')
            local_workspace = config.get('workspace', '/tmp/deploy/proxmox-local') if config else '/tmp/deploy/proxmox-local'

            transfer_artifacts_to_remote(ssh, local_workspace, remote_workspace, artifacts)
            runner = create_ssh_command_runner(ssh)
            variables = config.get('variables') if config else None

            ansible = AnsibleExecutor()
            try:
                ansible.execute(remote_workspace, artifacts, variables, command_runner=runner)
            except Exception as exc:
                logger.warning('Remote Ansible configuration skipped: %s', exc)

            docker = DockerExecutor()
            return docker.execute(remote_workspace, artifacts, variables, command_runner=runner)
        except Exception as exc:
            raise ProviderError(f'Remote Proxmox deployment failed: {exc}') from exc
        finally:
            close_ssh(ssh)

    def teardown(self, project, config=None):
        logger.info('Proxmox provider: destroying VMs')
        remote_config = resolve_remote_config(config)

        if remote_config and remote_config.is_remote():
            return self._teardown_remote(config, remote_config)

        terraform = TerraformExecutor()
        workspace = config.get('workspace', '/tmp/deploy/proxmox') if config else '/tmp/deploy/proxmox'
        try:
            return terraform.teardown(workspace, config.get('variables') if config else None)
        except Exception as exc:
            raise ProviderError(f'Proxmox teardown failed: {exc}') from exc

    def _teardown_remote(self, config, remote_config):
        ssh = None
        try:
            ssh = connect_ssh(remote_config)
            remote_workspace = get_remote_workspace(config, 'proxmox')
            runner = create_ssh_command_runner(ssh)
            terraform = TerraformExecutor()
            return terraform.teardown(remote_workspace, config.get('variables') if config else None, command_runner=runner)
        except Exception as exc:
            raise ProviderError(f'Remote Proxmox teardown failed: {exc}') from exc
        finally:
            close_ssh(ssh)

    def status(self, project, config=None):
        return {'provider': self.provider_name, 'status': 'active'}
