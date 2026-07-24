import logging
from typing import Any, Dict, List, Optional

from ....exceptions import DevopsException
from ...interfaces.logging import LoggingInterface


class BaseLoggingService(LoggingInterface):
    """Base logging service implementation."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.entries: List[Dict[str, Any]] = []

    def log_event(self, event: Dict[str, Any]) -> None:
        self.entries.append(event)
        self.logger.info('Logged event: %s', event)

    def query_logs(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        if not filters:
            return self.entries[:limit]
        result = [entry for entry in self.entries if all(entry.get(key) == value for key, value in filters.items())]
        self.logger.info('Queried %d logs', len(result))
        return result[:limit]

    def get_log_summary(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logs = self.query_logs(filters)
        summary = {
            'count': len(logs),
            'levels': {},
        }
        for entry in logs:
            level = entry.get('level', 'info')
            summary['levels'][level] = summary['levels'].get(level, 0) + 1
        self.logger.info('Computed log summary with %d entries', len(logs))
        return summary
