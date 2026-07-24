from abc import abstractmethod
from typing import Any, Dict, List, Optional

from .base import ServiceInterface
from ...exceptions import GitException


class GitInterface(ServiceInterface):
    """Abstract contract for Git operations.

    Responsibilities:
        - Provide generic version control operations.
        - Expose git primitives without binding to a provider.
    Excluded responsibilities:
        - Repository hosting-specific flows.
    """

    @abstractmethod
    def clone(self, repository_url: str, destination: str, depth: Optional[int] = None) -> None:
        """Clone a repository to a local destination."""
        raise GitException('clone not implemented')

    @abstractmethod
    def pull(self, repository_path: str, branch: Optional[str] = None) -> None:
        """Pull the latest changes for a repository."""
        raise GitException('pull not implemented')

    @abstractmethod
    def fetch(self, repository_path: str, remote: str = 'origin') -> None:
        """Fetch updates from a remote repository."""
        raise GitException('fetch not implemented')

    @abstractmethod
    def checkout(self, repository_path: str, branch: str) -> None:
        """Switch the working tree to a branch or revision."""
        raise GitException('checkout not implemented')

    @abstractmethod
    def commit(self, repository_path: str, message: str, author: Optional[str] = None) -> str:
        """Create a commit and return its hash."""
        raise GitException('commit not implemented')

    @abstractmethod
    def push(self, repository_path: str, remote: str = 'origin', branch: Optional[str] = None) -> None:
        """Push local commits to a remote repository."""
        raise GitException('push not implemented')

    @abstractmethod
    def list_branches(self, repository_path: str, remote: bool = False) -> List[str]:
        """Return the available branches."""
        raise GitException('list_branches not implemented')

    @abstractmethod
    def get_current_branch(self, repository_path: str) -> str:
        """Return the currently checked out branch."""
        raise GitException('get_current_branch not implemented')

    @abstractmethod
    def get_status(self, repository_path: str) -> Dict[str, Any]:
        """Return the repository working tree status."""
        raise GitException('get_status not implemented')
