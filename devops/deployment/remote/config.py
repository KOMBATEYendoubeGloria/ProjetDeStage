"""Remote deployment configuration — resolves connection parameters from models or explicit config."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ..exceptions import DeploymentValidationError

logger = logging.getLogger(__name__)


@dataclass
class RemoteConfig:
    """SSH connection parameters for remote deployment.

    Can be constructed explicitly or resolved from a deployment config dict
    containing either a ``deployment_target_id`` or explicit SSH fields.
    """

    host: str = ''
    port: int = 22
    username: str = ''
    private_key: str = ''
    password: str = ''
    passphrase: str = ''
    workspace: str = '/tmp/deploy/remote'

    # ------------------------------------------------------------------
    # Factory methods
    # ------------------------------------------------------------------

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> Optional['RemoteConfig']:
        """Build a RemoteConfig from a deployment config dict.

        Returns ``None`` if the config does not indicate a remote deployment.
        """
        if not _is_remote_config(config):
            return None

        host = config.get('host', '')
        username = config.get('ssh_user', config.get('username', ''))
        if not host or not username:
            return None

        return cls(
            host=host,
            port=int(config.get('ssh_port', config.get('port', 22))),
            username=username,
            private_key=config.get('ssh_key', config.get('private_key', '')),
            password=config.get('ssh_password', config.get('password', '')),
            passphrase=config.get('ssh_passphrase', config.get('passphrase', '')),
            workspace=config.get('remote_workspace', '/tmp/deploy/remote'),
        )

    @classmethod
    def from_deployment_target(cls, target, credential=None, remote_workspace: str = '/tmp/deploy/remote') -> 'RemoteConfig':
        """Build a RemoteConfig from a DeploymentTarget model instance.

        ``target`` is a ``devops.models.DeploymentTarget``.
        ``credential`` is an optional ``devops.models.SSHCredential``.
        If not provided, tries ``target.virtual_machine.ssh_credential``.
        """
        host = target.host or ''
        port = target.port or 22

        if credential is None and hasattr(target, 'virtual_machine') and target.virtual_machine:
            vm = target.virtual_machine
            if hasattr(vm, 'ssh_credential') and vm.ssh_credential:
                credential = vm.ssh_credential

        username = ''
        private_key = ''
        password = ''
        passphrase = ''

        if credential is not None:
            username = credential.username or ''
            private_key = credential.private_key or ''
            passphrase = credential.passphrase or ''

        return cls(
            host=host,
            port=int(port),
            username=username,
            private_key=private_key,
            password=password,
            passphrase=passphrase,
            workspace=remote_workspace,
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def is_remote(self) -> bool:
        """Return True if this config describes a remote target."""
        return bool(self.host and self.username)

    def validate(self) -> None:
        """Raise DeploymentValidationError if the remote config is incomplete."""
        if not self.host:
            raise DeploymentValidationError('Remote host is required')
        if not self.username:
            raise DeploymentValidationError('SSH username is required')

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dict (excluding sensitive fields)."""
        return {
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'has_private_key': bool(self.private_key),
            'has_password': bool(self.password),
            'workspace': self.workspace,
        }


def _is_remote_config(config: Dict[str, Any]) -> bool:
    """Detect whether a config dict indicates a remote deployment target."""
    if not config:
        return False
    if config.get('deployment_target_id'):
        return True
    if config.get('host') and (config.get('ssh_user') or config.get('username')):
        return True
    return False
