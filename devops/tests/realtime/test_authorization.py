"""Tests for AuthorizationService."""

from django.contrib.auth.models import AnonymousUser
from django.test import SimpleTestCase, TestCase

from devops.realtime.authorization import AuthorizationService


class AuthorizationServiceTests(SimpleTestCase):

    def setUp(self):
        self.auth = AuthorizationService()

    def test_anonymous_denied_deployment(self):
        self.assertFalse(self.auth.can_access_deployment(AnonymousUser(), 'abc'))

    def test_none_denied_deployment(self):
        self.assertFalse(self.auth.can_access_deployment(None, 'abc'))

    def test_authenticated_allowed_deployment(self):
        from unittest.mock import MagicMock
        user = MagicMock()
        user.is_authenticated = True
        self.assertTrue(self.auth.can_access_deployment(user, 'abc'))

    def test_anonymous_denied_project(self):
        self.assertFalse(self.auth.can_access_project(AnonymousUser(), 'proj'))

    def test_none_denied_project(self):
        self.assertFalse(self.auth.can_access_project(None, 'proj'))

    def test_authenticated_allowed_project(self):
        from unittest.mock import MagicMock
        user = MagicMock()
        user.is_authenticated = True
        self.assertTrue(self.auth.can_access_project(user, 'proj'))

    def test_user_can_access_own_channel(self):
        from unittest.mock import MagicMock
        user = MagicMock()
        user.is_authenticated = True
        user.pk = 42
        self.assertTrue(self.auth.can_access_user_channel(user, 42))

    def test_user_denied_other_channel(self):
        from unittest.mock import MagicMock
        user = MagicMock()
        user.is_authenticated = True
        user.pk = 42
        self.assertFalse(self.auth.can_access_user_channel(user, 99))

    def test_anonymous_denied_user_channel(self):
        self.assertFalse(self.auth.can_access_user_channel(AnonymousUser(), 1))
