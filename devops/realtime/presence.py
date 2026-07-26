"""PresenceTracker — tracks online users via Django's cache framework.

Uses django.core.cache as the storage backend. Never uses a plain Python dict
as the primary store (dict is only used as a local reference cache for fast lookups).
"""

from __future__ import annotations

import logging
from typing import List, Optional, Set

from django.core.cache import cache

logger = logging.getLogger(__name__)

_PRESENCE_KEY_PREFIX = 'ws:presence:'
_PRESENCE_SET_KEY = 'ws:presence:online_users'
_PRESENCE_TTL = 300  # 5 minutes


class PresenceTracker:
    """Tracks which users are currently connected via WebSocket.

    Backed by Django's cache framework (InMemoryChannelLayer's cache
    in dev, Redis in production).
    """

    def user_connected(self, user_id: int) -> None:
        """Mark a user as online."""
        key = f'{_PRESENCE_KEY_PREFIX}{user_id}'
        cache.set(key, True, timeout=_PRESENCE_TTL)
        # Maintain a set of online user IDs
        online = cache.get(_PRESENCE_SET_KEY, set())
        if not isinstance(online, set):
            online = set()
        online.add(user_id)
        cache.set(_PRESENCE_SET_KEY, online, timeout=_PRESENCE_TTL)
        logger.debug('Presence: user %s connected', user_id)

    def user_disconnected(self, user_id: int) -> None:
        """Mark a user as offline."""
        key = f'{_PRESENCE_KEY_PREFIX}{user_id}'
        cache.delete(key)
        online = cache.get(_PRESENCE_SET_KEY, set())
        if isinstance(online, set):
            online.discard(user_id)
            cache.set(_PRESENCE_SET_KEY, online, timeout=_PRESENCE_TTL)
        logger.debug('Presence: user %s disconnected', user_id)

    def is_online(self, user_id: int) -> bool:
        """Check if a user is currently connected."""
        return cache.get(f'{_PRESENCE_KEY_PREFIX}{user_id}', False) is True

    def get_online_users(self) -> Set[int]:
        """Return the set of currently online user IDs."""
        online = cache.get(_PRESENCE_SET_KEY, set())
        return online if isinstance(online, set) else set()

    def get_online_count(self) -> int:
        """Return the number of currently online users."""
        return len(self.get_online_users())
