from abc import abstractmethod
from typing import Any, Dict, List, Optional

from .base import ServiceInterface
from ...exceptions import DevopsException


class SecretInterface(ServiceInterface):
    """Abstract contract for secret management.

    Responsibilities:
        - Manage secret storage and retrieval.
    Excluded responsibilities:
        - Secret encryption implementation.
    """

    @abstractmethod
    def store_secret(self, data: Dict[str, Any]) -> str:
        """Store a secret and return its identifier."""
        raise DevopsException('store_secret not implemented')

    @abstractmethod
    def retrieve_secret(self, secret_id: str) -> Dict[str, Any]:
        """Retrieve secret metadata without exposing sensitive values."""
        raise DevopsException('retrieve_secret not implemented')

    @abstractmethod
    def list_secrets(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List secrets for a given project or scope."""
        raise DevopsException('list_secrets not implemented')

    @abstractmethod
    def delete_secret(self, secret_id: str) -> None:
        """Delete a secret."""
        raise DevopsException('delete_secret not implemented')
