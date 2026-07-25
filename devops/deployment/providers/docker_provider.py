"""Docker provider — deploys containers locally or on a Docker host."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..executors import AnsibleExecutor, DockerExecutor, TerraformExecutor
from ..exceptions import ProviderError
from .base import BaseProvider

logger = logging.getLogger(__name__)


class DockerProvider(BaseProvider):
    """Deploy applications as Docker containers.

    Uses DockerExecutor for container deployment. TerraformExecutor is used
    for optional Docker host provisioning. AnsibleExecutor is skipped for
    local Docker deployments.
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
        executor = DockerExecutor()
        workspace = config.get('workspace', '/tmp/deploy/docker') if config else '/tmp/deploy/docker'
        try:
            result = executor.execute(workspace, artifacts, config.get('variables') if config else None)
            return result
        except Exception as exc:
            raise ProviderError(f'Docker deployment failed: {exc}') from exc

    def teardown(self, project, config=None):
        logger.info('Docker provider: tearing down')
        executor = DockerExecutor()
        workspace = config.get('workspace', '/tmp/deploy/docker') if config else '/tmp/deploy/docker'
        return executor.teardown(workspace)

    def status(self, project, config=None):
        return {'provider': self.provider_name, 'status': 'active'}
