import json
import logging
import urllib.request
from typing import Any, Dict, List, Optional

from .base import BaseNotificationService
from ....exceptions import DevopsException


class WebhookNotificationService(BaseNotificationService):
    """Webhook notification implementation."""

    provider_name = 'webhook'

    supported_channels = ['webhook']

    def __init__(self, timeout: int = 10) -> None:
        super().__init__()
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)

    def _deliver(self, subject: str, message: str, recipients: List[str], metadata: Optional[Dict[str, Any]] = None) -> None:
        payload = json.dumps({
            'subject': subject,
            'message': message,
            'metadata': metadata or {},
        }).encode('utf-8')
        for endpoint in recipients:
            request = urllib.request.Request(endpoint, data=payload, headers={'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    self.logger.info('Webhook call to %s returned %s', endpoint, response.status)
            except Exception as exc:
                self.logger.error('Webhook delivery failed for %s: %s', endpoint, exc)
                raise DevopsException(str(exc)) from exc
