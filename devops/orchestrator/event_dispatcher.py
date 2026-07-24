"""Dispatch orchestrator events to listeners."""

from __future__ import annotations

from typing import Any, Callable, Dict, List


class EventDispatcher:
    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[[Any], None]]] = {}

    def register(self, event_name: str, listener: Callable[[Any], None]) -> None:
        self._listeners.setdefault(event_name, []).append(listener)

    def dispatch(self, event_name: str, event: Any) -> None:
        for listener in self._listeners.get(event_name, []):
            listener(event)
