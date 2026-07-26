"""AuthorizationService — checks access permissions for WebSocket channels.

Contains NO business logic beyond access control. Consumers delegate
all authorization checks here.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AuthorizationService:
    """Checks whether a user is authorized to access a WebSocket channel."""

    def can_access_deployment(self, user, deployment_id: str) -> bool:
        """Check if a user can view/subscribe to a deployment.

        Anonymous users are denied. Authenticated users are granted
        (fine-grained per-deployment ACL can be added later).
        """
        if user is None or not user.is_authenticated:
            return False
        return True

    def can_access_project(self, user, project_id: str) -> bool:
        """Check if a user can view/subscribe to a project channel."""
        if user is None or not user.is_authenticated:
            return False
        return True

    def can_access_user_channel(self, user, target_user_id: int) -> bool:
        """Check if a user can view another user's private channel.

        Users can always access their own channel.
        """
        if user is None or not user.is_authenticated:
            return False
        return user.pk == target_user_id
