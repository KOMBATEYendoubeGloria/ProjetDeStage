import logging
from typing import Any, Dict, List, Optional

from ....exceptions import DevopsException
from ...interfaces.environment import EnvironmentInterface


class BaseEnvironmentService(EnvironmentInterface):
    """Base environment management implementation."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._environments: Dict[str, Dict[str, Any]] = {}

    def list_environments(self) -> List[Dict[str, Any]]:
        result = list(self._environments.values())
        self.logger.info('Listed %d environments', len(result))
        return result

    def get_environment(self, environment_id: str) -> Dict[str, Any]:
        try:
            environment = self._environments[environment_id]
        except KeyError as exc:
            self.logger.error('Environment not found: %s', environment_id)
            raise DevopsException(f'Environment not found: {environment_id}') from exc
        self.logger.info('Retrieved environment %s', environment_id)
        return environment

    def create_environment(self, data: Dict[str, Any]) -> str:
        environment_id = data.get('id') or data.get('name')
        if not environment_id:
            raise DevopsException('Environment data must include an id or name')
        self._environments[environment_id] = data
        self.logger.info('Created environment %s', environment_id)
        return environment_id

    def update_environment(self, environment_id: str, data: Dict[str, Any]) -> None:
        if environment_id not in self._environments:
            raise DevopsException(f'Environment not found: {environment_id}')
        self._environments[environment_id].update(data)
        self.logger.info('Updated environment %s', environment_id)

    def delete_environment(self, environment_id: str) -> None:
        if environment_id not in self._environments:
            raise DevopsException(f'Environment not found: {environment_id}')
        del self._environments[environment_id]
        self.logger.info('Deleted environment %s', environment_id)
