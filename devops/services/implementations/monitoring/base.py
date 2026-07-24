import logging
from typing import Any, Dict, List, Optional

from ....exceptions import DevopsException
from ...interfaces.monitoring import MonitoringInterface


class BaseMonitoringService(MonitoringInterface):
    """Base monitoring service implementation."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.events: List[Dict[str, Any]] = []

    def get_metrics(self, target_id: Optional[str] = None, metric_names: Optional[List[str]] = None) -> Dict[str, Any]:
        result = {
            key: value
            for key, value in self.metrics.items()
            if (target_id is None or value.get('target_id') == target_id) and (metric_names is None or key in metric_names)
        }
        self.logger.info('Collected metrics for target %s', target_id)
        return result

    def get_status(self, target_id: Optional[str] = None) -> Dict[str, Any]:
        status = {
            'target_id': target_id,
            'healthy': True,
            'metrics': self.get_metrics(target_id),
        }
        self.logger.info('Retrieved status for target %s', target_id)
        return status

    def get_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        alerts = [alert for alert in self.events if severity is None or alert.get('severity') == severity]
        self.logger.info('Retrieved %d alerts', len(alerts))
        return alerts

    def get_events(self, target_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        selected = [event for event in self.events if target_id is None or event.get('target_id') == target_id]
        self.logger.info('Retrieved %d events for target %s', min(len(selected), limit), target_id)
        return selected[:limit]
