"""In-memory thread-safe publish/subscribe event bus."""

from __future__ import annotations

import logging
import threading
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class EventBus:
    """Thread-safe publish/subscribe event bus.

    Subscribers register callbacks for named event types.
    Publishing calls all registered callbacks synchronously.
    History is NOT stored here — persistence is handled by the monitoring layer.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[str, dict], None]]] = {}
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, callback: Callable[[str, dict], None]) -> None:
        """Register a callback for an event type."""
        with self._lock:
            self._subscribers.setdefault(event_type, []).append(callback)
        logger.debug('EventBus: subscribed to %s', event_type)

    def unsubscribe(self, event_type: str, callback: Callable[[str, dict], None]) -> None:
        """Remove a previously registered callback."""
        with self._lock:
            subs = self._subscribers.get(event_type, [])
            if callback in subs:
                subs.remove(callback)

    def publish(self, event_type: str, payload: dict) -> None:
        """Publish an event to all registered subscribers.

        Callbacks are invoked synchronously in the current thread.
        Each callback receives (event_type, payload).
        """
        with self._lock:
            subscribers = list(self._subscribers.get(event_type, []))

        for callback in subscribers:
            try:
                callback(event_type, payload)
            except Exception:
                logger.exception('EventBus: error in subscriber for %s', event_type)

    def clear(self) -> None:
        """Remove all subscribers."""
        with self._lock:
            self._subscribers.clear()
