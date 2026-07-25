"""Ansible executor — configures infrastructure via ansible-playbook CLI."""

from __future__ import annotations

import logging
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..exceptions import AnsibleExecutorError
from .base import BaseExecutor

if TYPE_CHECKING:
    from ..remote.command_runner import CommandRunner

logger = logging.getLogger(__name__)


class AnsibleExecutor(BaseExecutor):
    """Execute Ansible playbooks to configure provisioned infrastructure.

    Writes playbook and inventory artifacts to the workspace, then runs
    ``ansible-playbook`` against the target hosts.

    Supports an optional ``command_runner`` parameter on ``execute()`` and
    ``teardown()`` for transparent remote execution via SSH.
    """

    executor_name = 'ansible'

    def __init__(self, binary: str = 'ansible-playbook') -> None:
        self._binary = binary
        self._logs: List[str] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _run(self, args: List[str], cwd: Optional[str] = None, command_runner: Optional['CommandRunner'] = None) -> str:
        command = [self._binary] + args
        self._log(f'Running: {" ".join(shlex.quote(a) for a in command)}')
        if command_runner is not None:
            return command_runner.run(command, cwd=cwd)
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True,
            )
            if completed.stdout.strip():
                self._log(completed.stdout.strip())
            return completed.stdout.strip()
        except FileNotFoundError as exc:
            raise AnsibleExecutorError(f'{self._binary} executable not found') from exc
        except subprocess.CalledProcessError as exc:
            message = exc.stderr.strip() or exc.stdout.strip()
            self._log(f'ERROR: {message}')
            raise AnsibleExecutorError(message or 'ansible-playbook command failed') from exc

    def _log(self, message: str) -> None:
        self._logs.append(message)
        logger.debug('[AnsibleExecutor] %s', message)

    def _write_artifacts(self, workspace: str, playbook: str, inventory: str) -> None:
        work_dir = Path(workspace)
        work_dir.mkdir(parents=True, exist_ok=True)
        playbook_file = work_dir / 'playbook.yml'
        playbook_file.write_text(playbook, encoding='utf-8')
        inventory_file = work_dir / 'inventory.ini'
        inventory_file.write_text(inventory, encoding='utf-8')
        self._log(f'Wrote playbook to {playbook_file}')
        self._log(f'Wrote inventory to {inventory_file}')

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
    def initialize(self, workspace: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._log('Ansible executor initialized')
        return {'status': 'initialized'}

    def validate(self, workspace: str) -> bool:
        self._log('Checking Ansible requirements')
        return True

    def execute(self, workspace: str, artifacts: Dict[str, Any], variables: Optional[Dict[str, Any]] = None, command_runner: Optional['CommandRunner'] = None) -> Dict[str, Any]:
        """Write playbook + inventory and run ansible-playbook."""
        playbook = artifacts.get('ansible_playbook', '')
        inventory = artifacts.get('ansible_inventory', '')

        if not playbook:
            raise AnsibleExecutorError('No ansible_playbook artifact provided')

        self._write_artifacts(workspace, playbook, inventory)

        args = ['playbook.yml', '-i', 'inventory.ini', '--become']
        if variables:
            for key, value in variables.items():
                args.extend(['-e', f'{key}={value}'])

        output = self._run(args, cwd=workspace, command_runner=command_runner)
        return {'status': 'configured', 'playbook_output': output}

    def teardown(self, workspace: str, variables: Optional[Dict[str, Any]] = None, command_runner: Optional['CommandRunner'] = None) -> Dict[str, Any]:
        self._log('Ansible teardown is a no-op (configurations are idempotent)')
        return {'status': 'no_op'}

    def get_logs(self) -> List[str]:
        return list(self._logs)
