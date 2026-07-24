from abc import abstractmethod
from typing import Any, Dict, List, Optional

from .base import ServiceInterface
from ...exceptions import DevopsException


class NotificationInterface(ServiceInterface):
    """Abstract contract for notifications.

    Responsibilities:
        - Send generic notifications independent of channel.
    Excluded responsibilities:
        - Channel-specific transport logic.
    """

    @abstractmethod
    def send_notification(self, subject: str, message: str, recipients: List[str], metadata: Optional[Dict[str, Any]] = None) -> None:
        """Send a notification to recipients."""
        raise DevopsException('send_notification not implemented')

    @abstractmethod
    def list_channels(self) -> List[Dict[str, Any]]:
        """Return supported notification channels."""
        raise DevopsException('list_channels not implemented')
