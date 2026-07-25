"""VMware provider — provisions VMs on vSphere and deploys via SSH."""

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


class VMwareProvider(BaseProvider):
    """Deploy applications on VMware vSphere virtual machines.

    Full pipeline: Terraform provisions VMs via the vsphere provider,
    Ansible configures them, Docker deploys containers.

    Supports remote deployment via SSH when config contains host/ssh_user.
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
        remote_config = resolve_remote_config(config)

        if remote_config and remote_config.is_remote():
            return self._deploy_remote(artifacts, config, remote_config)

        return self._deploy_local(artifacts, config)

    def _deploy_local(self, artifacts, config):
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

    def _deploy_remote(self, artifacts, config, remote_config):
        ssh = None
        try:
            ssh = connect_ssh(remote_config)
            remote_workspace = get_remote_workspace(config, 'vmware')
            local_workspace = config.get('workspace', '/tmp/deploy/vmware-local') if config else '/tmp/deploy/vmware-local'

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
            raise ProviderError(f'Remote VMware deployment failed: {exc}') from exc
        finally:
            close_ssh(ssh)

    def teardown(self, project, config=None):
        logger.info('VMware provider: destroying VMs')
        remote_config = resolve_remote_config(config)

        if remote_config and remote_config.is_remote():
            return self._teardown_remote(config, remote_config)

        terraform = TerraformExecutor()
        workspace = config.get('workspace', '/tmp/deploy/vmware') if config else '/tmp/deploy/vmware'
        try:
            return terraform.teardown(workspace, config.get('variables') if config else None)
        except Exception as exc:
            raise ProviderError(f'VMware teardown failed: {exc}') from exc

    def _teardown_remote(self, config, remote_config):
        ssh = None
        try:
            ssh = connect_ssh(remote_config)
            remote_workspace = get_remote_workspace(config, 'vmware')
            runner = create_ssh_command_runner(ssh)
            terraform = TerraformExecutor()
            return terraform.teardown(remote_workspace, config.get('variables') if config else None, command_runner=runner)
        except Exception as exc:
            raise ProviderError(f'Remote VMware teardown failed: {exc}') from exc
        finally:
            close_ssh(ssh)

    def status(self, project, config=None):
        return {'provider': self.provider_name, 'status': 'active'}
