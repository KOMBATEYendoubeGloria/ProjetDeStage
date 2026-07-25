"""Terraform executor — provisions infrastructure via terraform CLI."""

from __future__ import annotations

import json
import logging
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..exceptions import TerraformExecutorError
from .base import BaseExecutor

logger = logging.getLogger(__name__)


class TerraformExecutor(BaseExecutor):
    """Execute Terraform commands to provision and manage infrastructure.

    Handles init, validate, plan, apply, destroy, and output operations.
    Writes artifacts to a workspace directory before execution.
    """

    executor_name = 'terraform'

    def __init__(self, binary: str = 'terraform') -> None:
        self._binary = binary
        self._logs: List[str] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _run(self, args: List[str], cwd: Optional[str] = None) -> str:
        command = [self._binary] + args
        self._log(f'Running: {" ".join(shlex.quote(a) for a in command)}')
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
            raise TerraformExecutorError(f'{self._binary} executable not found') from exc
        except subprocess.CalledProcessError as exc:
            message = exc.stderr.strip() or exc.stdout.strip()
            self._log(f'ERROR: {message}')
            raise TerraformExecutorError(message or 'terraform command failed') from exc

    def _log(self, message: str) -> None:
        self._logs.append(message)
        logger.debug('[TerraformExecutor] %s', message)

    def _write_artifacts(self, workspace: str, terraform_content: str) -> None:
        """Write terraform content to main.tf in the workspace."""
        work_dir = Path(workspace)
        work_dir.mkdir(parents=True, exist_ok=True)
        tf_file = work_dir / 'main.tf'
        tf_file.write_text(terraform_content, encoding='utf-8')
        self._log(f'Wrote terraform config to {tf_file}')

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
    def initialize(self, workspace: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._log('Initializing Terraform workspace')
        backend_config = config.get('backend_config', {}) if config else {}
        args = ['init', '-input=false']
        for key, value in backend_config.items():
            args.extend(['-backend-config', f'{key}={value}'])
        self._run(args, cwd=workspace)
        return {'status': 'initialized'}

    def validate(self, workspace: str) -> bool:
        self._log('Validating Terraform configuration')
        self._run(['validate', '-no-color'], cwd=workspace)
        return True

    def plan(self, workspace: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._log('Running Terraform plan')
        args = ['plan', '-input=false', '-no-color']
        if variables:
            for key, value in variables.items():
                args.extend(['-var', f'{key}={value}'])
        output = self._run(args, cwd=workspace)
        return {'plan': output}

    def execute(self, workspace: str, artifacts: Dict[str, Any], variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Write terraform content, init, and apply."""
        terraform_content = artifacts.get('terraform', '')
        if not terraform_content:
            raise TerraformExecutorError('No terraform artifact provided')

        self._write_artifacts(workspace, terraform_content)
        self.initialize(workspace)
        self.plan(workspace, variables)

        self._log('Applying Terraform configuration')
        args = ['apply', '-input=false', '-auto-approve', '-no-color']
        if variables:
            for key, value in variables.items():
                args.extend(['-var', f'{key}={value}'])
        output = self._run(args, cwd=workspace)

        tf_output = self.output(workspace)
        return {'status': 'applied', 'apply_output': output, 'outputs': tf_output}

    def teardown(self, workspace: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._log('Destroying Terraform infrastructure')
        args = ['destroy', '-input=false', '-auto-approve', '-no-color']
        if variables:
            for key, value in variables.items():
                args.extend(['-var', f'{key}={value}'])
        output = self._run(args, cwd=workspace)
        return {'status': 'destroyed', 'destroy_output': output}

    def output(self, workspace: str) -> Dict[str, Any]:
        raw = self._run(['output', '-json'], cwd=workspace)
        return json.loads(raw) if raw else {}

    def get_logs(self) -> List[str]:
        return list(self._logs)
