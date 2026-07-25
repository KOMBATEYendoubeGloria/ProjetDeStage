"""Docker executor — deploys containers via docker CLI."""

from __future__ import annotations

import logging
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..exceptions import DockerExecutorError
from .base import BaseExecutor

if TYPE_CHECKING:
    from ..remote.command_runner import CommandRunner

logger = logging.getLogger(__name__)


class DockerExecutor(BaseExecutor):
    """Execute Docker commands to build and deploy containers.

    Writes Dockerfile and docker-compose artifacts to the workspace, then
    runs ``docker compose up`` (or ``docker build`` / ``docker run``).

    Supports an optional ``command_runner`` parameter on ``execute()`` and
    ``teardown()`` for transparent remote execution via SSH.
    """

    executor_name = 'docker'

    def __init__(self, compose_binary: str = 'docker') -> None:
        self._binary = compose_binary
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
            raise DockerExecutorError(f'{self._binary} executable not found') from exc
        except subprocess.CalledProcessError as exc:
            message = exc.stderr.strip() or exc.stdout.strip()
            self._log(f'ERROR: {message}')
            raise DockerExecutorError(message or 'docker command failed') from exc

    def _log(self, message: str) -> None:
        self._logs.append(message)
        logger.debug('[DockerExecutor] %s', message)

    def _write_artifacts(self, workspace: str, dockerfile: str, compose: str, environment: str = '') -> None:
        work_dir = Path(workspace)
        work_dir.mkdir(parents=True, exist_ok=True)
        if dockerfile:
            df_file = work_dir / 'Dockerfile'
            df_file.write_text(dockerfile, encoding='utf-8')
            self._log(f'Wrote Dockerfile to {df_file}')
        if compose:
            compose_file = work_dir / 'docker-compose.yml'
            compose_file.write_text(compose, encoding='utf-8')
            self._log(f'Wrote docker-compose.yml to {compose_file}')
        if environment:
            env_file = work_dir / '.env'
            env_file.write_text(environment, encoding='utf-8')
            self._log(f'Wrote .env to {env_file}')

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
    def initialize(self, workspace: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._log('Docker executor initialized')
        return {'status': 'initialized'}

    def validate(self, workspace: str) -> bool:
        self._log('Checking Docker availability')
        self._run(['info', '--format', '{{.ServerVersion}}'])
        return True

    def execute(self, workspace: str, artifacts: Dict[str, Any], variables: Optional[Dict[str, Any]] = None, command_runner: Optional['CommandRunner'] = None) -> Dict[str, Any]:
        """Write artifacts and deploy with docker compose."""
        dockerfile = artifacts.get('dockerfile', '')
        compose = artifacts.get('docker_compose', '')
        environment = artifacts.get('environment', '')

        if not dockerfile and not compose:
            raise DockerExecutorError('No docker or docker_compose artifact provided')

        self._write_artifacts(workspace, dockerfile, compose, environment)

        if compose:
            self._log('Deploying with docker compose')
            output = self._run(['compose', '-f', 'docker-compose.yml', 'up', '-d'], cwd=workspace, command_runner=command_runner)
            return {'status': 'deployed', 'compose_output': output}

        if dockerfile:
            project_name = artifacts.get('metadata', {}).get('project_name', 'app')
            self._log(f'Building Docker image: {project_name}')
            self._run(['build', '-t', f'{project_name}:latest', '.'], cwd=workspace, command_runner=command_runner)
            self._log(f'Running container: {project_name}')
            output = self._run(['run', '-d', '--name', project_name, f'{project_name}:latest'], cwd=workspace, command_runner=command_runner)
            return {'status': 'deployed', 'container_id': output}

        return {'status': 'no_op'}

    def teardown(self, workspace: str, variables: Optional[Dict[str, Any]] = None, command_runner: Optional['CommandRunner'] = None) -> Dict[str, Any]:
        self._log('Stopping and removing Docker containers')
        try:
            output = self._run(['compose', '-f', 'docker-compose.yml', 'down'], cwd=workspace, command_runner=command_runner)
            return {'status': 'stopped', 'down_output': output}
        except DockerExecutorError:
            self._log('docker compose down failed, attempting cleanup')
            return {'status': 'cleanup_attempted'}

    def get_logs(self) -> List[str]:
        return list(self._logs)
