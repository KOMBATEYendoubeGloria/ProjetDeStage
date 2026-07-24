import logging
from abc import abstractmethod
from typing import Any, Dict, List, Optional

from ....exceptions import DevopsException
from ...interfaces.notification import NotificationInterface


class BaseNotificationService(NotificationInterface):
    """Base notification implementation."""

    supported_channels: List[str] = []

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def _deliver(self, subject: str, message: str, recipients: List[str], metadata: Optional[Dict[str, Any]] = None) -> None:
        raise DevopsException('Delivery method not implemented')

    def send_notification(self, subject: str, message: str, recipients: List[str], metadata: Optional[Dict[str, Any]] = None) -> None:
        if not recipients:
            raise DevopsException('Recipients are required')
        self.logger.info('Sending notification to %s', recipients)
        self._deliver(subject, message, recipients, metadata)

    def list_channels(self) -> List[Dict[str, Any]]:
        return [{'name': channel} for channel in self.supported_channels]
