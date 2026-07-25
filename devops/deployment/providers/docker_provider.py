"""Docker provider — deploys containers locally or on a remote Docker host."""

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


class DockerProvider(BaseProvider):
    """Deploy applications as Docker containers.

    Uses DockerExecutor for container deployment. TerraformExecutor is used
    for optional Docker host provisioning. AnsibleExecutor is skipped for
    local Docker deployments.

    Supports remote deployment via SSH when config contains host/ssh_user.
    """

    provider_name = 'docker'
    display_name = 'Docker (Local / Remote Host)'

    def get_required_executors(self):
        return ['docker']

    def provision(self, project, artifacts, config=None):
        logger.info('Docker provider: provisioning')
        terraform = TerraformExecutor()
        terraform_content = artifacts.get('terraform', '')
        if terraform_content:
            workspace = config.get('workspace', '/tmp/deploy/docker') if config else '/tmp/deploy/docker'
            return terraform.execute(workspace, artifacts, config.get('variables') if config else None)
        return {'status': 'no_provisioning_needed'}

    def deploy(self, project, artifacts, config=None):
        logger.info('Docker provider: deploying')
        remote_config = resolve_remote_config(config)

        if remote_config and remote_config.is_remote():
            return self._deploy_remote(artifacts, config, remote_config)

        return self._deploy_local(artifacts, config)

    def _deploy_local(self, artifacts, config):
        executor = DockerExecutor()
        workspace = config.get('workspace', '/tmp/deploy/docker') if config else '/tmp/deploy/docker'
        try:
            return executor.execute(workspace, artifacts, config.get('variables') if config else None)
        except Exception as exc:
            raise ProviderError(f'Docker deployment failed: {exc}') from exc

    def _deploy_remote(self, artifacts, config, remote_config):
        ssh = None
        try:
            ssh = connect_ssh(remote_config)
            remote_workspace = get_remote_workspace(config, 'docker')
            local_workspace = config.get('workspace', '/tmp/deploy/docker-local') if config else '/tmp/deploy/docker-local'

            transfer_artifacts_to_remote(ssh, local_workspace, remote_workspace, artifacts)
            runner = create_ssh_command_runner(ssh)

            executor = DockerExecutor()
            result = executor.execute(remote_workspace, artifacts, config.get('variables') if config else None, command_runner=runner)
            return result
        except Exception as exc:
            raise ProviderError(f'Remote Docker deployment failed: {exc}') from exc
        finally:
            close_ssh(ssh)

    def teardown(self, project, config=None):
        logger.info('Docker provider: tearing down')
        remote_config = resolve_remote_config(config)

        if remote_config and remote_config.is_remote():
            return self._teardown_remote(config, remote_config)

        executor = DockerExecutor()
        workspace = config.get('workspace', '/tmp/deploy/docker') if config else '/tmp/deploy/docker'
        return executor.teardown(workspace)

    def _teardown_remote(self, config, remote_config):
        ssh = None
        try:
            ssh = connect_ssh(remote_config)
            remote_workspace = get_remote_workspace(config, 'docker')
            runner = create_ssh_command_runner(ssh)
            executor = DockerExecutor()
            return executor.teardown(remote_workspace, command_runner=runner)
        except Exception as exc:
            raise ProviderError(f'Remote Docker teardown failed: {exc}') from exc
        finally:
            close_ssh(ssh)

    def status(self, project, config=None):
        return {'provider': self.provider_name, 'status': 'active'}
