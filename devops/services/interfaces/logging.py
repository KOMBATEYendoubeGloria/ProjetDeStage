from abc import abstractmethod
from typing import Any, Dict, List, Optional

from .base import ServiceInterface
from ...exceptions import DevopsException


class LoggingInterface(ServiceInterface):
    """Abstract contract for log persistence and retrieval.

    Responsibilities:
        - Record and query structured logs.
    Excluded responsibilities:
        - Concrete storage backends and indexing.
    """

    @abstractmethod
    def log_event(self, event: Dict[str, Any]) -> None:
        """Record an event to the logging backend."""
        raise DevopsException('log_event not implemented')

    @abstractmethod
    def query_logs(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Query logs with optional filters."""
        raise DevopsException('query_logs not implemented')

    @abstractmethod
    def get_log_summary(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return aggregated log metrics."""
        raise DevopsException('get_log_summary not implemented')
