import logging
from typing import Any, Dict, List

from ....exceptions import DevopsException
from ...interfaces.repository import RepositoryInterface


class BaseRepositoryService(RepositoryInterface):
    """Base repository metadata service implementation."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._repositories: Dict[str, Dict[str, Any]] = {}

    def list_repositories(self) -> List[Dict[str, Any]]:
        result = list(self._repositories.values())
        self.logger.info('Listed %d repositories', len(result))
        return result

    def get_repository(self, repository_id: str) -> Dict[str, Any]:
        try:
            repo = self._repositories[repository_id]
        except KeyError as exc:
            self.logger.error('Repository not found: %s', repository_id)
            raise DevopsException(f'Repository not found: {repository_id}') from exc
        self.logger.info('Retrieved repository %s', repository_id)
        return repo

    def add_repository(self, metadata: Dict[str, Any]) -> str:
        repository_id = metadata.get('id') or metadata.get('name')
        if not repository_id:
            raise DevopsException('Repository metadata must include an id or name')
        self._repositories[repository_id] = metadata
        self.logger.info('Added repository %s', repository_id)
        return repository_id

    def remove_repository(self, repository_id: str) -> None:
        if repository_id not in self._repositories:
            raise DevopsException(f'Repository not found: {repository_id}')
        del self._repositories[repository_id]
        self.logger.info('Removed repository %s', repository_id)
