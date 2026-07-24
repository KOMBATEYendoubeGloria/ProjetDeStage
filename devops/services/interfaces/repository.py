from abc import abstractmethod
from typing import Any, Dict, List

from .base import ServiceInterface
from ...exceptions import DevopsException


class RepositoryInterface(ServiceInterface):
    """Abstract contract for repository metadata management.

    Responsibilities:
        - Manage repository metadata and registration.
    Excluded responsibilities:
        - Lower-level Git transport operations.
    """

    @abstractmethod
    def list_repositories(self) -> List[Dict[str, Any]]:
        """Return known repositories."""
        raise DevopsException('list_repositories not implemented')

    @abstractmethod
    def get_repository(self, repository_id: str) -> Dict[str, Any]:
        """Return metadata for a repository."""
        raise DevopsException('get_repository not implemented')

    @abstractmethod
    def add_repository(self, metadata: Dict[str, Any]) -> str:
        """Register a repository and return its identifier."""
        raise DevopsException('add_repository not implemented')

    @abstractmethod
    def remove_repository(self, repository_id: str) -> None:
        """Unregister a repository."""
        raise DevopsException('remove_repository not implemented')
