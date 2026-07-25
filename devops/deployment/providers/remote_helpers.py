"""Remote deployment helpers — SSH connection and artifact transfer for providers."""

from __future__ import annotations

import logging
import os
import tempfile
from typing import Any, Dict, Optional

from ..exceptions import ProviderError
from ..remote.config import RemoteConfig

logger = logging.getLogger(__name__)


def resolve_remote_config(config: Optional[Dict[str, Any]]) -> Optional[RemoteConfig]:
    """Resolve a RemoteConfig from the deployment config dict, if present."""
    if not config:
        return None
    return RemoteConfig.from_config(config)


def connect_ssh(remote_config: RemoteConfig):
    """Establish an SSH connection and return a BaseSSHService instance.

    Import is deferred to avoid hard dependency on paramiko at module level.
    """
    try:
        from devops.services.implementations.ssh.base import BaseSSHService
    except ImportError:
        raise ProviderError('SSH services require paramiko. Install it with: pip install paramiko')

    ssh = BaseSSHService()
    connect_kwargs = {
        'host': remote_config.host,
        'port': remote_config.port,
        'username': remote_config.username,
    }
    if remote_config.private_key:
        # Write private key to a temp file for paramiko
        key_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pem')
        key_file.write(remote_config.private_key.encode('utf-8'))
        key_file.close()
        connect_kwargs['key'] = key_file.name
    elif remote_config.password:
        connect_kwargs['password'] = remote_config.password

    ssh.connect(**connect_kwargs)
    logger.info('SSH connected to %s@%s:%s', remote_config.username, remote_config.host, remote_config.port)
    return ssh


def transfer_artifacts_to_remote(
    ssh_service: Any,
    local_workspace: str,
    remote_workspace: str,
    artifacts: Dict[str, Any],
) -> None:
    """Write artifacts locally, then transfer them to the remote host."""
    from ..remote.transfer import transfer_workspace

    os.makedirs(local_workspace, exist_ok=True)
    _write_artifacts_locally(local_workspace, artifacts)
    transfer_workspace(ssh_service, local_workspace, remote_workspace)


def _write_artifacts_locally(workspace: str, artifacts: Dict[str, Any]) -> None:
    """Write all relevant artifacts to the local workspace for transfer."""
    from pathlib import Path
    work_dir = Path(workspace)
    work_dir.mkdir(parents=True, exist_ok=True)

    file_map = {
        'terraform': 'main.tf',
        'dockerfile': 'Dockerfile',
        'docker_compose': 'docker-compose.yml',
        'environment': '.env',
        'ansible_playbook': 'playbook.yml',
        'ansible_inventory': 'inventory.ini',
    }
    for artifact_key, filename in file_map.items():
        content = artifacts.get(artifact_key, '')
        if content:
            (work_dir / filename).write_text(content, encoding='utf-8')
            logger.debug('Wrote local artifact: %s/%s', workspace, filename)


def create_ssh_command_runner(ssh_service: Any):
    """Create an SSHCommandRunner from a connected SSH service."""
    from ..remote.command_runner import SSHCommandRunner
    return SSHCommandRunner(ssh_service)


def close_ssh(ssh_service: Any) -> None:
    """Safely close an SSH connection."""
    try:
        ssh_service.close()
    except Exception as exc:
        logger.warning('Error closing SSH connection: %s', exc)


def get_remote_workspace(config: Optional[Dict[str, Any]], provider_name: str) -> str:
    """Get the remote workspace path from config, or use a provider-specific default."""
    if config:
        return config.get('remote_workspace', f'/tmp/deploy/{provider_name}')
    return f'/tmp/deploy/{provider_name}'
