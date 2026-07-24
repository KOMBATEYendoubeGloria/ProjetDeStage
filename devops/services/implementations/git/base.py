import json
import logging
import subprocess
from typing import Any, Dict, List, Optional

from ...interfaces.git import GitInterface
from ....exceptions import GitException


class BaseGitService(GitInterface):
    """Provider-agnostic Git service implementation."""

    provider_name: str = 'generic'

    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token
        self.logger = logging.getLogger(self.__class__.__name__)

    def _run_git(self, args: List[str], cwd: Optional[str] = None) -> str:
        command = ['git'] + args
        self.logger.debug('Executing git command: %s', ' '.join(command))
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            message = exc.stderr.strip() or exc.stdout.strip()
            self.logger.error('Git command failed: %s', message)
            raise GitException(message or 'git command failed') from exc
        return completed.stdout.strip()

    def clone(self, repository_url: str, destination: str, depth: Optional[int] = None) -> None:
        args = ['clone', repository_url, destination]
        if depth is not None:
            args.extend(['--depth', str(depth)])
        self._run_git(args)
        self.logger.info('Cloned repository %s into %s', repository_url, destination)

    def pull(self, repository_path: str, branch: Optional[str] = None) -> None:
        args = ['pull']
        if branch:
            args.append('origin')
            args.append(branch)
        self._run_git(args, cwd=repository_path)
        self.logger.info('Pulled repository %s branch %s', repository_path, branch or 'default')

    def fetch(self, repository_path: str, remote: str = 'origin') -> None:
        self._run_git(['fetch', remote], cwd=repository_path)
        self.logger.info('Fetched remote %s for repository %s', remote, repository_path)

    def checkout(self, repository_path: str, branch: str) -> None:
        self._run_git(['checkout', branch], cwd=repository_path)
        self.logger.info('Checked out branch %s in repository %s', branch, repository_path)

    def commit(self, repository_path: str, message: str, author: Optional[str] = None) -> str:
        args = ['commit', '-am', message]
        if author:
            args.extend(['--author', author])
        output = self._run_git(args, cwd=repository_path)
        self.logger.info('Created commit in %s', repository_path)
        return output

    def push(self, repository_path: str, remote: str = 'origin', branch: Optional[str] = None) -> None:
        args = ['push', remote]
        if branch:
            args.append(branch)
        self._run_git(args, cwd=repository_path)
        self.logger.info('Pushed repository %s to %s %s', repository_path, remote, branch or '')

    def list_branches(self, repository_path: str, remote: bool = False) -> List[str]:
        args = ['branch', '--format', '%(refname:short)']
        if remote:
            args.append('--remotes')
        output = self._run_git(args, cwd=repository_path)
        return [line.strip() for line in output.splitlines() if line.strip()]

    def get_current_branch(self, repository_path: str) -> str:
        return self._run_git(['rev-parse', '--abbrev-ref', 'HEAD'], cwd=repository_path)

    def get_status(self, repository_path: str) -> Dict[str, Any]:
        output = self._run_git(['status', '--porcelain', '--branch'], cwd=repository_path)
        return {
            'raw': output,
            'lines': [line for line in output.splitlines() if line.strip()],
        }
