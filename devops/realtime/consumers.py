"""WebSocket consumers — handle real-time connections for the frontend.

Consumers contain NO business logic. They only handle:
- Authentication/authorization (via middleware + AuthorizationService)
- Group subscription/unsubscription
- Message emission
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .authorization import AuthorizationService
from .groups import deployment_group_name, project_group_name, user_group_name
from .presence import PresenceTracker
from .protocol import ClientActions, CloseCodes, EventTypes, PROTOCOL_VERSION

logger = logging.getLogger(__name__)

_authorization = AuthorizationService()
_presence = PresenceTracker()


class _BaseConsumer(AsyncJsonWebsocketConsumer):
    """Shared consumer logic — message formatting, pong, error handling."""

    async def send_event(self, event_type: str, payload: Dict[str, Any], **extra) -> None:
        """Send a protocol-compliant event message."""
        import uuid
        from datetime import datetime, timezone
        message = {
            'version': PROTOCOL_VERSION,
            'event': event_type,
            'event_id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'payload': payload,
            **extra,
        }
        await self.send(text_data=json.dumps(message))

    async def send_error(self, message: str, code: int = CloseCodes.INTERNAL_ERROR) -> None:
        """Send an error event to the client."""
        await self.send_event(EventTypes.ERROR, {'message': message, 'code': code})

    async def send_ack(self, action: str, data: Dict[str, Any] = None) -> None:
        """Send an action acknowledgement."""
        await self.send_event(EventTypes.ACTION_ACKNOWLEDGED, {
            'action': action,
            'data': data or {},
        })


class DeploymentConsumer(_BaseConsumer):
    """WebSocket consumer for deployment-specific real-time updates.

    Route: ws/deployments/<deployment_id>/
    """

    async def connect(self):
        self.deployment_id = self.scope['url_route']['kwargs']['deployment_id']
        self.user = self.scope.get('user')

        if not _authorization.can_access_deployment(self.user, self.deployment_id):
            await self.close(code=CloseCodes.NOT_AUTHORIZED)
            return

        self.group_name = deployment_group_name(self.deployment_id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_event(EventTypes.CONNECTION_ESTABLISHED, {
            'deployment_id': self.deployment_id,
        })

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        action = content.get('action', '')
        if action == ClientActions.PING:
            await self.send_event(EventTypes.HEARTBEAT_PONG, {})
        elif action == ClientActions.CANCEL_DEPLOYMENT:
            await self.send_ack(action, {'deployment_id': self.deployment_id})
        else:
            await self.send_error(f'Unknown action: {action}')

    async def websocket_message(self, event):
        """Handler for messages sent to the deployment group."""
        message = event.get('message', {})
        await self.send(text_data=json.dumps(message))


class ProjectConsumer(_BaseConsumer):
    """WebSocket consumer for project-wide deployment updates.

    Route: ws/projects/<project_id>/
    """

    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.user = self.scope.get('user')

        if not _authorization.can_access_project(self.user, self.project_id):
            await self.close(code=CloseCodes.NOT_AUTHORIZED)
            return

        self.group_name = project_group_name(self.project_id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_event(EventTypes.CONNECTION_ESTABLISHED, {
            'project_id': self.project_id,
        })

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        action = content.get('action', '')
        if action == ClientActions.PING:
            await self.send_event(EventTypes.HEARTBEAT_PONG, {})
        else:
            await self.send_error(f'Unknown action: {action}')

    async def websocket_message(self, event):
        message = event.get('message', {})
        await self.send(text_data=json.dumps(message))


class UserConsumer(_BaseConsumer):
    """WebSocket consumer for user-specific notifications.

    Route: ws/user/
    """

    async def connect(self):
        self.user = self.scope.get('user')
        if self.user is None or self.user.is_anonymous:
            await self.close(code=CloseCodes.AUTH_FAILED)
            return

        self.user_id = self.user.pk
        self.group_name = user_group_name(self.user_id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        _presence.user_connected(self.user_id)
        await self.send_event(EventTypes.CONNECTION_ESTABLISHED, {
            'user_id': self.user_id,
        })

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, 'user_id'):
            _presence.user_disconnected(self.user_id)

    async def receive_json(self, content, **kwargs):
        action = content.get('action', '')
        if action == ClientActions.PING:
            await self.send_event(EventTypes.HEARTBEAT_PONG, {})
        else:
            await self.send_error(f'Unknown action: {action}')

    async def websocket_message(self, event):
        message = event.get('message', {})
        await self.send(text_data=json.dumps(message))
