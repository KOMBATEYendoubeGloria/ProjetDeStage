import logging
from typing import Any, Dict, List, Optional

from ....exceptions import DevopsException
from ...interfaces.artifact import ArtifactInterface


class BaseArtifactService(ArtifactInterface):
    """Base artifact service implementation."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._artifacts: Dict[str, Dict[str, Any]] = {}

    def store_artifact(self, metadata: Dict[str, Any], payload: Optional[Any] = None) -> str:
        artifact_id = metadata.get('id') or metadata.get('name')
        if not artifact_id:
            raise DevopsException('Artifact metadata must include an id or name')
        self._artifacts[artifact_id] = {
            'metadata': metadata,
            'payload': payload,
        }
        self.logger.info('Stored artifact %s', artifact_id)
        return artifact_id

    def retrieve_artifact(self, artifact_id: str) -> Dict[str, Any]:
        try:
            artifact = self._artifacts[artifact_id]
        except KeyError as exc:
            self.logger.error('Artifact not found: %s', artifact_id)
            raise DevopsException(f'Artifact not found: {artifact_id}') from exc
        self.logger.info('Retrieved artifact %s', artifact_id)
        return artifact

    def list_artifacts(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        artifacts = [artifact for artifact in self._artifacts.values() if not project_id or artifact['metadata'].get('project_id') == project_id]
        self.logger.info('Listed %d artifacts', len(artifacts))
        return artifacts

    def delete_artifact(self, artifact_id: str) -> None:
        if artifact_id not in self._artifacts:
            raise DevopsException(f'Artifact not found: {artifact_id}')
        del self._artifacts[artifact_id]
        self.logger.info('Deleted artifact %s', artifact_id)
