"""WebSocket protocol constants.

All protocol versioning, event types, client actions, and close codes
are centralized here. No literal strings should be scattered elsewhere.
"""

from __future__ import annotations

from enum import Enum

PROTOCOL_VERSION = '1.0'
HEARTBEAT_INTERVAL_SECONDS = 30


class EventTypes(str, Enum):
    """All WebSocket event types sent from server to client."""

    # Deployment lifecycle
    DEPLOYMENT_QUEUED = 'deployment.queued'
    DEPLOYMENT_STARTED = 'deployment.started'
    DEPLOYMENT_WAITING = 'deployment.waiting'
    DEPLOYMENT_COMPLETED = 'deployment.completed'
    DEPLOYMENT_FAILED = 'deployment.failed'
    DEPLOYMENT_CANCELLED = 'deployment.cancelled'
    DEPLOYMENT_WARNING = 'deployment.warning'
    DEPLOYMENT_INFO = 'deployment.info'
    DEPLOYMENT_CANCEL_REQUESTED = 'deployment.cancel_requested'

    # Stage progress
    STAGE_STARTED = 'stage.started'
    STAGE_COMPLETED = 'stage.completed'
    PROGRESS_UPDATED = 'progress.updated'

    # Logs
    LOG_CREATED = 'log.created'

    # Rollback
    ROLLBACK_STARTED = 'rollback.started'
    ROLLBACK_COMPLETED = 'rollback.completed'

    # System
    SYSTEM_NOTIFICATION = 'system.notification'
    CONNECTION_ESTABLISHED = 'connection.established'
    ACTION_ACKNOWLEDGED = 'action.acknowledged'
    HEARTBEAT_PONG = 'pong'
    ERROR = 'error'


class ClientActions(str, Enum):
    """All client-to-server action types."""

    PING = 'ping'
    SUBSCRIBE_DEPLOYMENT = 'subscribe.deployment'
    UNSUBSCRIBE_DEPLOYMENT = 'unsubscribe.deployment'
    SUBSCRIBE_PROJECT = 'subscribe.project'
    UNSUBSCRIBE_PROJECT = 'unsubscribe.project'
    CANCEL_DEPLOYMENT = 'cancel.deployment'


class CloseCodes(int, Enum):
    """WebSocket close codes for the DevOps protocol."""

    NORMAL_CLOSURE = 1000
    GOING_AWAY = 1001
    PROTOCOL_ERROR = 1002
    UNSUPPORTED_DATA = 1003
    NO_STATUS_RECEIVED = 1005
    ABNORMAL_CLOSURE = 1006
    INVALID_FRAME_PAYLOAD = 1007
    POLICY_VIOLATION = 1008
    MESSAGE_TOO_BIG = 1009
    MANDATORY_EXTENSION = 1010
    INTERNAL_ERROR = 1011
    AUTH_FAILED = 4001
    AUTH_EXPIRED = 4002
    NOT_AUTHORIZED = 4003
    RATE_LIMITED = 4029
