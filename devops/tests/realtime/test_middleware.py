"""Tests for JWTWebSocketMiddleware."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from devops.realtime.middleware import JWTWebSocketMiddleware


class JWTWebSocketMiddlewareTests(SimpleTestCase):

    def _make_scope(self, query_string='', path='/ws/test/'):
        return {
            'type': 'websocket',
            'query_string': query_string.encode('utf-8'),
            'path': path,
        }

    def test_extract_token_present(self):
        middleware = JWTWebSocketMiddleware(None)
        scope = self._make_scope(query_string='token=abc123')
        token = middleware._extract_token(scope)
        self.assertEqual(token, 'abc123')

    def test_extract_token_missing(self):
        middleware = JWTWebSocketMiddleware(None)
        scope = self._make_scope(query_string='')
        token = middleware._extract_token(scope)
        self.assertIsNone(token)

    def test_extract_token_empty_query(self):
        middleware = JWTWebSocketMiddleware(None)
        scope = self._make_scope(query_string='')
        self.assertIsNone(middleware._extract_token(scope))

    def test_extract_token_multiple_params(self):
        middleware = JWTWebSocketMiddleware(None)
        scope = self._make_scope(query_string='foo=bar&token=xyz789')
        self.assertEqual(middleware._extract_token(scope), 'xyz789')

    def test_non_websocket_passthrough(self):
        async def dummy(scope, receive, send):
            return 'ok'

        middleware = JWTWebSocketMiddleware(dummy)
        scope = {'type': 'http'}
        result = None

        async def run():
            nonlocal result
            result = await middleware(scope, None, None)

        import asyncio
        asyncio.get_event_loop().run_until_complete(run())
        self.assertEqual(result, 'ok')
