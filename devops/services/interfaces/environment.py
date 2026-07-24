from abc import abstractmethod
from typing import Any, Dict, List, Optional

from .base import ServiceInterface
from ...exceptions import DevopsException


class EnvironmentInterface(ServiceInterface):
    """Abstract contract for environment management.

    Responsibilities:
        - Manage lifecycle of environments for deployment contexts.
    Excluded responsibilities:
        - Environment provisioning.
    """

    @abstractmethod
    def list_environments(self) -> List[Dict[str, Any]]:
        """Return available environments."""
        raise DevopsException('list_environments not implemented')

    @abstractmethod
    def get_environment(self, environment_id: str) -> Dict[str, Any]:
        """Return environment metadata."""
        raise DevopsException('get_environment not implemented')

    @abstractmethod
    def create_environment(self, data: Dict[str, Any]) -> str:
        """Create a new environment."""
        raise DevopsException('create_environment not implemented')

    @abstractmethod
    def update_environment(self, environment_id: str, data: Dict[str, Any]) -> None:
        """Update environment metadata."""
        raise DevopsException('update_environment not implemented')

    @abstractmethod
    def delete_environment(self, environment_id: str) -> None:
        """Delete an environment."""
        raise DevopsException('delete_environment not implemented')
