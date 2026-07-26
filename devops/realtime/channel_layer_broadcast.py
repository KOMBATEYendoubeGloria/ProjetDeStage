"""ChannelLayerBroadcaster — concrete broadcaster using Django Channels.

This is the ONLY file in the realtime package that imports from channels.layers.
All channel layer interaction is isolated here.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from channels.layers import get_channel_layer

from .broadcast import EventBroadcaster
from .groups import user_group_name
from .protocol import PROTOCOL_VERSION

logger = logging.getLogger(__name__)


class ChannelLayerBroadcaster(EventBroadcaster):
    """Broadcasts events through the Django Channels layer.

    Wraps get_channel_layer() and formats all messages to the protocol spec.
    """

    def __init__(self, channel_layer=None):
        self._channel_layer = channel_layer or get_channel_layer()

    @property
    def channel_layer(self):
        return self._channel_layer

    async def broadcast_to_group(self, group_name: str, event_type: str, payload: Dict[str, Any]) -> None:
        """Send an event to all members of a channel layer group."""
        message = self._build_message(event_type, payload)
        await self._channel_layer.group_send(group_name, {
            'type': 'websocket.message',
            'message': message,
        })

    async def broadcast_to_user(self, user_id: int, event_type: str, payload: Dict[str, Any]) -> None:
        """Send an event to all connections of a specific user."""
        group = user_group_name(user_id)
        await self.broadcast_to_group(group, event_type, payload)

    async def broadcast_all(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Send an event to the system-wide broadcast group."""
        message = self._build_message(event_type, payload)
        await self._channel_layer.group_send('system.all', {
            'type': 'websocket.message',
            'message': message,
        })

    def _build_message(self, event_type: str, payload: Dict[str, Any], **extra) -> Dict[str, Any]:
        """Build a protocol-compliant message dict."""
        return {
            'version': PROTOCOL_VERSION,
            'event': event_type,
            'event_id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'payload': payload,
            **extra,
        }
