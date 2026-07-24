import json
import logging
import shlex
import subprocess
from typing import Any, Dict, List, Optional

from ....exceptions import InfrastructureException
from ...interfaces.infrastructure import InfrastructureInterface


class BaseInfrastructureService(InfrastructureInterface):
    """Base implementation for infrastructure toolchains."""

    binary: str

    def __init__(self, binary: str) -> None:
        self.binary = binary
        self.logger = logging.getLogger(self.__class__.__name__)

    def _run(self, args: List[str], cwd: Optional[str] = None) -> str:
        command = [self.binary] + args
        self.logger.debug('Running infrastructure command: %s', ' '.join(shlex.quote(item) for item in command))
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True,
            )
        except FileNotFoundError as exc:
            raise InfrastructureException(f'{self.binary} executable not found') from exc
        except subprocess.CalledProcessError as exc:
            message = exc.stderr.strip() or exc.stdout.strip()
            self.logger.error('Infrastructure command failed: %s', message)
            raise InfrastructureException(message or 'infrastructure command failed') from exc
        return completed.stdout.strip()

    def init(self, workspace_path: str, backend_config: Optional[Dict[str, Any]] = None) -> None:
        args = ['init']
        if backend_config:
            for key, value in backend_config.items():
                args.extend(['-backend-config', f'{key}={value}'])
        self._run(args, cwd=workspace_path)
        self.logger.info('Initialized workspace %s', workspace_path)

    def validate(self, workspace_path: str) -> None:
        self._run(['validate'], cwd=workspace_path)
        self.logger.info('Validated infrastructure in %s', workspace_path)

    def plan(self, workspace_path: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        args = ['plan', '-input=false', '-no-color']
        if variables:
            for key, value in variables.items():
                args.extend(['-var', f'{key}={value}'])
        output = self._run(args, cwd=workspace_path)
        return {'plan': output}

    def apply(self, workspace_path: str, variables: Optional[Dict[str, Any]] = None, auto_approve: bool = False) -> Dict[str, Any]:
        args = ['apply', '-input=false', '-no-color']
        if auto_approve:
            args.append('-auto-approve')
        if variables:
            for key, value in variables.items():
                args.extend(['-var', f'{key}={value}'])
        output = self._run(args, cwd=workspace_path)
        return {'apply': output}

    def destroy(self, workspace_path: str, variables: Optional[Dict[str, Any]] = None, auto_approve: bool = False) -> Dict[str, Any]:
        args = ['destroy', '-input=false', '-no-color']
        if auto_approve:
            args.append('-auto-approve')
        if variables:
            for key, value in variables.items():
                args.extend(['-var', f'{key}={value}'])
        output = self._run(args, cwd=workspace_path)
        return {'destroy': output}

    def output(self, workspace_path: str) -> Dict[str, Any]:
        output = self._run(['output', '-json'], cwd=workspace_path)
        self.logger.info('Read infrastructure outputs from %s', workspace_path)
        return json.loads(output) if output else {}

    def workspace(self, workspace_path: str, name: str) -> None:
        try:
            self._run(['workspace', 'select', name], cwd=workspace_path)
            self.logger.info('Selected workspace %s', name)
        except InfrastructureException:
            self._run(['workspace', 'new', name], cwd=workspace_path)
            self.logger.info('Created workspace %s', name)
