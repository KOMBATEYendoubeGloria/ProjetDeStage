"""EventBroadcaster — abstract interface for broadcasting WebSocket messages.

This ABC defines the contract for how events are sent to channel groups.
The only concrete implementation is ChannelLayerBroadcaster.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class EventBroadcaster(ABC):
    """Abstract broadcaster — defines how events reach WebSocket clients."""

    @abstractmethod
    async def broadcast_to_group(self, group_name: str, event_type: str, payload: Dict[str, Any]) -> None:
        """Send an event to all members of a channel layer group."""
        raise NotImplementedError

    @abstractmethod
    async def broadcast_to_user(self, user_id: int, event_type: str, payload: Dict[str, Any]) -> None:
        """Send an event to all connections of a specific user."""
        raise NotImplementedError

    @abstractmethod
    async def broadcast_all(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Send an event to all connected clients (system-wide broadcast)."""
        raise NotImplementedError
