"""DevOps realtime WebSocket package.

This package provides real-time WebSocket communication for deployment monitoring.
It bridges the Phase 11 EventBus to WebSocket clients via Django Channels.

Architecture::

    EventBus → EventBridge → EventBroadcaster (ABC) → ChannelLayerBroadcaster
    → Channel Layer → Consumers → Frontend

No business logic lives here. This layer only forwards events.
"""

__all__ = []
