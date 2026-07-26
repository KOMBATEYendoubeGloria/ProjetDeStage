"""Tests for WebSocket consumers."""

from unittest.mock import AsyncMock, MagicMock, patch

from django.test import SimpleTestCase

from devops.realtime.consumers import _BaseConsumer, DeploymentConsumer, ProjectConsumer, UserConsumer
from devops.realtime.protocol import EventTypes, CloseCodes


class BaseConsumerTests(SimpleTestCase):

    def test_base_consumer_is_abstract_enough(self):
        self.assertTrue(issubclass(DeploymentConsumer, _BaseConsumer))
        self.assertTrue(issubclass(ProjectConsumer, _BaseConsumer))
        self.assertTrue(issubclass(UserConsumer, _BaseConsumer))


class DeploymentConsumerTests(SimpleTestCase):

    def test_has_connect(self):
        self.assertTrue(hasattr(DeploymentConsumer, 'connect'))

    def test_has_disconnect(self):
        self.assertTrue(hasattr(DeploymentConsumer, 'disconnect'))

    def test_has_receive_json(self):
        self.assertTrue(hasattr(DeploymentConsumer, 'receive_json'))

    def test_has_websocket_message(self):
        self.assertTrue(hasattr(DeploymentConsumer, 'websocket_message'))


class ProjectConsumerTests(SimpleTestCase):

    def test_has_required_methods(self):
        self.assertTrue(hasattr(ProjectConsumer, 'connect'))
        self.assertTrue(hasattr(ProjectConsumer, 'disconnect'))
        self.assertTrue(hasattr(ProjectConsumer, 'receive_json'))
        self.assertTrue(hasattr(ProjectConsumer, 'websocket_message'))


class UserConsumerTests(SimpleTestCase):

    def test_has_required_methods(self):
        self.assertTrue(hasattr(UserConsumer, 'connect'))
        self.assertTrue(hasattr(UserConsumer, 'disconnect'))
        self.assertTrue(hasattr(UserConsumer, 'receive_json'))
        self.assertTrue(hasattr(UserConsumer, 'websocket_message'))
