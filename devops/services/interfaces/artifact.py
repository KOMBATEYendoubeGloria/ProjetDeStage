from abc import abstractmethod
from typing import Any, Dict, List, Optional

from .base import ServiceInterface
from ...exceptions import DevopsException


class ArtifactInterface(ServiceInterface):
    """Abstract contract for artifact storage and retrieval.

    Responsibilities:
        - Manage artifacts produced by deployments and pipelines.
    Excluded responsibilities:
        - Artifact storage implementation details.
    """

    @abstractmethod
    def store_artifact(self, metadata: Dict[str, Any], payload: Optional[Any] = None) -> str:
        """Store an artifact and return its identifier."""
        raise DevopsException('store_artifact not implemented')

    @abstractmethod
    def retrieve_artifact(self, artifact_id: str) -> Dict[str, Any]:
        """Retrieve artifact metadata and payload location."""
        raise DevopsException('retrieve_artifact not implemented')

    @abstractmethod
    def list_artifacts(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List artifacts, optionally filtered by project."""
        raise DevopsException('list_artifacts not implemented')

    @abstractmethod
    def delete_artifact(self, artifact_id: str) -> None:
        """Delete an artifact."""
        raise DevopsException('delete_artifact not implemented')
