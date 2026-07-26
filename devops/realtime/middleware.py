"""JWT WebSocket middleware — authenticates WebSocket connections via query token."""

from __future__ import annotations

import logging
from typing import Callable, Optional

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

logger = logging.getLogger(__name__)


class JWTWebSocketMiddleware(BaseMiddleware):
    """Authenticates WebSocket connections using ?token=<jwt> query parameter.

    Sets scope['user'] on success. AnonymousUser on failure or missing token.
    """

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'websocket':
            return await super().__call__(scope, receive, send)

        token = self._extract_token(scope)
        scope['user'] = await self._authenticate(token) if token else await self._get_anonymous()
        return await super().__call__(scope, receive, send)

    def _extract_token(self, scope) -> Optional[str]:
        """Extract token from query string: ws://...?token=<jwt>."""
        query_string = scope.get('query_string', b'').decode('utf-8')
        if not query_string:
            return None
        params = dict(param.split('=', 1) for param in query_string.split('&') if '=' in param)
        return params.get('token')

    @database_sync_to_async
    def _authenticate(self, token: str):
        """Validate JWT and return the user, or anonymous on failure."""
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return self._get_user_by_id(user_id)
        except (TokenError, InvalidToken, KeyError) as exc:
            logger.debug('JWT auth failed: %s', exc)
            return self._get_anonymous_sync()

    @database_sync_to_async
    def _get_anonymous(self):
        return self._get_anonymous_sync()

    def _get_user_by_id(self, user_id: int):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return self._get_anonymous_sync()

    @staticmethod
    def _get_anonymous_sync():
        from django.contrib.auth.models import AnonymousUser
        return AnonymousUser()
