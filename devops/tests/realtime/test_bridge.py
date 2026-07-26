"""Tests for EventBridge."""

from unittest.mock import AsyncMock, MagicMock, patch

from django.test import SimpleTestCase

from devops.realtime.bridge import EventBridge, _EVENT_TYPE_MAP
from devops.realtime.protocol import EventTypes


class EventBridgeTests(SimpleTestCase):

    def test_event_type_map_contains_key_events(self):
        self.assertIn('deployment.queued', _EVENT_TYPE_MAP)
        self.assertIn('deployment.started', _EVENT_TYPE_MAP)
        self.assertIn('deployment.completed', _EVENT_TYPE_MAP)
        self.assertIn('deployment.failed', _EVENT_TYPE_MAP)
        self.assertIn('deployment.cancelled', _EVENT_TYPE_MAP)
        self.assertIn('deployment.phase_changed', _EVENT_TYPE_MAP)

    def test_event_type_map_values_are_event_types(self):
        for ws_type in _EVENT_TYPE_MAP.values():
            self.assertEqual(ws_type.value, ws_type)

    def test_bridge_stores_references(self):
        bus = MagicMock()
        broadcaster = MagicMock()
        bridge = EventBridge(bus, broadcaster)
        self.assertIs(bridge.broadcaster, broadcaster)

    def test_connect_subscribes_to_bus(self):
        bus = MagicMock()
        broadcaster = MagicMock()
        bridge = EventBridge(bus, broadcaster)
        bridge.connect()
        self.assertTrue(bus.subscribe.called)

    def test_disconnect_unsubscribes(self):
        bus = MagicMock()
        broadcaster = MagicMock()
        bridge = EventBridge(bus, broadcaster)
        bridge.connect()
        bridge.disconnect()
        self.assertEqual(len(bridge._callbacks), 0)
