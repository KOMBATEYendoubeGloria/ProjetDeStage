import logging
from typing import Any, Dict, List, Optional

from ....exceptions import DevopsException
from ...interfaces.secret import SecretInterface


class BaseSecretService(SecretInterface):
    """Base secret management implementation."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._secrets: Dict[str, Dict[str, Any]] = {}

    def store_secret(self, data: Dict[str, Any]) -> str:
        secret_id = data.get('id') or data.get('name')
        if not secret_id:
            raise DevopsException('Secret data must include an id or name')
        self._secrets[secret_id] = data
        self.logger.info('Stored secret %s', secret_id)
        return secret_id

    def retrieve_secret(self, secret_id: str) -> Dict[str, Any]:
        try:
            secret = self._secrets[secret_id]
        except KeyError as exc:
            self.logger.error('Secret not found: %s', secret_id)
            raise DevopsException(f'Secret not found: {secret_id}') from exc
        self.logger.info('Retrieved secret %s', secret_id)
        return secret

    def list_secrets(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        secrets = [secret for secret in self._secrets.values() if not project_id or secret.get('project_id') == project_id]
        self.logger.info('Listed %d secrets', len(secrets))
        return secrets

    def delete_secret(self, secret_id: str) -> None:
        if secret_id not in self._secrets:
            raise DevopsException(f'Secret not found: {secret_id}')
        del self._secrets[secret_id]
        self.logger.info('Deleted secret %s', secret_id)
