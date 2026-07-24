from abc import abstractmethod
from typing import Any, Dict, List, Optional

from .base import ServiceInterface
from ...exceptions import DevopsException


class MonitoringInterface(ServiceInterface):
    """Abstract contract for monitoring and observability.

    Responsibilities:
        - Provide access to metrics, health, alerts, and events.
    Excluded responsibilities:
        - Monitoring backend implementation details.
    """

    @abstractmethod
    def get_metrics(self, target_id: Optional[str] = None, metric_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Return metrics for a target or collection."""
        raise DevopsException('get_metrics not implemented')

    @abstractmethod
    def get_status(self, target_id: Optional[str] = None) -> Dict[str, Any]:
        """Return health or status data."""
        raise DevopsException('get_status not implemented')

    @abstractmethod
    def get_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return active alerts."""
        raise DevopsException('get_alerts not implemented')

    @abstractmethod
    def get_events(self, target_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Return observed events."""
        raise DevopsException('get_events not implemented')
