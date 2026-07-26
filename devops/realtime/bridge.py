"""EventBridge — connects Phase 11 EventBus to the WebSocket broadcaster.

Listens to EventBus events and transforms them into WebSocket messages
via the EventBroadcaster. This is the glue between the deployment engine
and the real-time layer.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

from .broadcast import EventBroadcaster
from .groups import deployment_group_name, project_group_name
from .protocol import EventTypes

logger = logging.getLogger(__name__)

# Mapping from Phase 11 EventBus event types to Phase 12 WebSocket event types.
_EVENT_TYPE_MAP: Dict[str, str] = {
    'deployment.queued': EventTypes.DEPLOYMENT_QUEUED,
    'deployment.started': EventTypes.DEPLOYMENT_STARTED,
    'deployment.phase_changed': EventTypes.PROGRESS_UPDATED,
    'deployment.completed': EventTypes.DEPLOYMENT_COMPLETED,
    'deployment.failed': EventTypes.DEPLOYMENT_FAILED,
    'deployment.cancelled': EventTypes.DEPLOYMENT_CANCELLED,
    'deployment.cancel_requested': EventTypes.DEPLOYMENT_CANCEL_REQUESTED,
    'deployment.finished': EventTypes.DEPLOYMENT_COMPLETED,
    'deployment.error': EventTypes.DEPLOYMENT_FAILED,
}


class EventBridge:
    """Bridges EventBus events to WebSocket broadcasts.

    Subscribes to EventBus events, transforms them, and broadcasts
    via the EventBroadcaster to the appropriate channel groups.
    """

    def __init__(self, event_bus, broadcaster: EventBroadcaster):
        self._event_bus = event_bus
        self._broadcaster = broadcaster
        self._callbacks: list = []

    @property
    def broadcaster(self) -> EventBroadcaster:
        return self._broadcaster

    def connect(self) -> None:
        """Subscribe to all relevant EventBus events."""
        for event_type in _EVENT_TYPE_MAP:
            callback = self._make_callback(event_type)
            self._event_bus.subscribe(event_type, callback)
            self._callbacks.append((event_type, callback))
        logger.info('EventBridge: connected to EventBus (%d event types)', len(self._callbacks))

    def disconnect(self) -> None:
        """Unsubscribe from all EventBus events."""
        for event_type, callback in self._callbacks:
            self._event_bus.unsubscribe(event_type, callback)
        self._callbacks.clear()
        logger.info('EventBridge: disconnected from EventBus')

    def _make_callback(self, source_event_type: str) -> Callable[[str, dict], None]:
        """Create a callback that bridges a specific event type."""
        def _callback(event_type: str, payload: dict) -> None:
            import asyncio
            ws_event_type = _EVENT_TYPE_MAP.get(source_event_type, source_event_type)
            deployment_id = payload.get('deployment_id', '')
            project_id = payload.get('project_id', '')

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(
                        self._broadcast(ws_event_type, deployment_id, project_id, payload)
                    )
                else:
                    loop.run_until_complete(
                        self._broadcast(ws_event_type, deployment_id, project_id, payload)
                    )
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    self._broadcast(ws_event_type, deployment_id, project_id, payload)
                )

        return _callback

    async def _broadcast(
        self,
        event_type: str,
        deployment_id: str,
        project_id: str,
        payload: dict,
    ) -> None:
        """Broadcast event to the relevant channel groups."""
        try:
            if deployment_id:
                group = deployment_group_name(deployment_id)
                await self._broadcaster.broadcast_to_group(group, event_type, payload)

            if project_id:
                group = project_group_name(project_id)
                await self._broadcaster.broadcast_to_group(group, event_type, payload)

        except Exception:
            logger.exception('EventBridge: failed to broadcast %s', event_type)
