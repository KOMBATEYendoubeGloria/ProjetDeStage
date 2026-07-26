"""Tests for PresenceTracker."""

from django.test import TestCase, override_settings

from devops.realtime.presence import PresenceTracker


@override_settings(SECURE_SSL_REDIRECT=False)
class PresenceTrackerTests(TestCase):

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.tracker = PresenceTracker()

    def test_user_connected(self):
        self.tracker.user_connected(1)
        self.assertTrue(self.tracker.is_online(1))

    def test_user_disconnected(self):
        self.tracker.user_connected(1)
        self.tracker.user_disconnected(1)
        self.assertFalse(self.tracker.is_online(1))

    def test_is_online_false_when_never_connected(self):
        self.assertFalse(self.tracker.is_online(999))

    def test_get_online_users(self):
        self.tracker.user_connected(1)
        self.tracker.user_connected(2)
        online = self.tracker.get_online_users()
        self.assertIn(1, online)
        self.assertIn(2, online)

    def test_get_online_count(self):
        self.tracker.user_connected(10)
        self.assertEqual(self.tracker.get_online_count(), 1)

    def test_disconnect_removes_from_online(self):
        self.tracker.user_connected(5)
        self.tracker.user_disconnect(5) if hasattr(self.tracker, 'user_disconnect') else self.tracker.user_disconnected(5)
        self.assertEqual(self.tracker.get_online_count(), 0)

    def test_multiple_users(self):
        for uid in [1, 2, 3]:
            self.tracker.user_connected(uid)
        self.assertEqual(self.tracker.get_online_count(), 3)
