"""Tests for CancellationToken and CancellationError."""

import threading
import time

from django.test import SimpleTestCase

from devops.deployment.async_engine.cancellation import CancellationToken, CancellationError


class CancellationTokenTests(SimpleTestCase):

    def test_initial_state_not_cancelled(self):
        token = CancellationToken()
        self.assertFalse(token.cancelled)
        self.assertFalse(token.is_cancelled)

    def test_cancel_sets_flag(self):
        token = CancellationToken()
        token.cancel()
        self.assertTrue(token.cancelled)
        self.assertTrue(token.is_cancelled)

    def test_throw_if_cancelled_raises_when_cancelled(self):
        token = CancellationToken()
        token.cancel()
        with self.assertRaises(CancellationError):
            token.throw_if_cancelled()

    def test_throw_if_cancelled_passes_when_not_cancelled(self):
        token = CancellationToken()
        token.throw_if_cancelled()

    def test_cancel_is_thread_safe(self):
        token = CancellationToken()
        errors = []

        def canceller():
            time.sleep(0.01)
            token.cancel()

        t = threading.Thread(target=canceller)
        t.start()
        for _ in range(100):
            _ = token.cancelled
        t.join()
        self.assertTrue(token.cancelled)

    def test_is_cancelled_alias(self):
        token = CancellationToken()
        self.assertEqual(token.is_cancelled, token.cancelled)


class CancellationErrorTests(SimpleTestCase):

    def test_is_exception(self):
        exc = CancellationError('test')
        self.assertIsInstance(exc, Exception)
        self.assertEqual(str(exc), 'test')
