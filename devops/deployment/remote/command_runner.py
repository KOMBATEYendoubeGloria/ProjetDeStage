"""Command runner abstraction — transparent local/remote command execution."""

from __future__ import annotations

import logging
import shlex
import subprocess
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..exceptions import ExecutorError

logger = logging.getLogger(__name__)


class CommandRunner(ABC):
    """Abstract interface for executing shell commands.

    Two implementations exist:
    - ``LocalCommandRunner``: wraps ``subprocess.run`` (current behavior).
    - ``SSHCommandRunner``: delegates to ``BaseSSHService.execute``.
    """

    @abstractmethod
    def run(self, command: List[str], cwd: Optional[str] = None) -> str:
        """Execute a command and return stdout. Raise on non-zero exit."""
        raise NotImplementedError

    @abstractmethod
    def run_raw(self, command: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        """Execute a command and return {stdout, stderr, exit_code}."""
        raise NotImplementedError


class LocalCommandRunner(CommandRunner):
    """Execute commands locally via ``subprocess.run``."""

    def __init__(self, binary_prefix: Optional[str] = None):
        self._prefix = binary_prefix
        self._logs: List[str] = []

    def run(self, command: List[str], cwd: Optional[str] = None) -> str:
        result = self.run_raw(command, cwd)
        if result['exit_code'] != 0:
            message = result['stderr'].strip() or result['stdout'].strip()
            raise ExecutorError(message or f'Command failed: {command[0]}')
        return result['stdout'].strip()

    def run_raw(self, command: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        full_command = command
        if self._prefix:
            full_command = [self._prefix] + command

        self._log(f'Running: {" ".join(shlex.quote(a) for a in full_command)}')
        try:
            completed = subprocess.run(
                full_command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
            )
            return {
                'stdout': completed.stdout,
                'stderr': completed.stderr,
                'exit_code': completed.returncode,
            }
        except FileNotFoundError as exc:
            raise ExecutorError(f'{full_command[0]} executable not found') from exc

    def get_logs(self) -> List[str]:
        return list(self._logs)

    def _log(self, message: str) -> None:
        self._logs.append(message)
        logger.debug('[LocalCommandRunner] %s', message)


class SSHCommandRunner(CommandRunner):
    """Execute commands on a remote host via ``BaseSSHService``.

    Reuses the existing SSH infrastructure without duplicating it.
    """

    def __init__(self, ssh_service: Any):
        """``ssh_service`` is a ``BaseSSHService`` instance (already connected)."""
        self._ssh = ssh_service
        self._logs: List[str] = []

    def run(self, command: List[str], cwd: Optional[str] = None) -> str:
        result = self.run_raw(command, cwd)
        if result['exit_code'] != 0:
            message = result['stderr'].strip() or result['stdout'].strip()
            raise ExecutorError(message or f'Remote command failed: {command[0]}')
        return result['stdout'].strip()

    def run_raw(self, command: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        shell_command = ' '.join(shlex.quote(a) for a in command)
        if cwd:
            shell_command = f'cd {shlex.quote(cwd)} && {shell_command}'

        self._log(f'SSH: {shell_command}')
        result = self._ssh.execute(shell_command)
        self._log(f'SSH exit_code={result.get("exit_code", -1)}')
        return {
            'stdout': result.get('stdout', ''),
            'stderr': result.get('stderr', ''),
            'exit_code': result.get('exit_code', -1),
        }

    def get_logs(self) -> List[str]:
        return list(self._logs)

    def _log(self, message: str) -> None:
        self._logs.append(message)
        logger.debug('[SSHCommandRunner] %s', message)
