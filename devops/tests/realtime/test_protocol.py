"""Tests for protocol constants."""

from django.test import SimpleTestCase

from devops.realtime.protocol import (
    PROTOCOL_VERSION,
    HEARTBEAT_INTERVAL_SECONDS,
    EventTypes,
    ClientActions,
    CloseCodes,
)


class ProtocolConstantsTests(SimpleTestCase):

    def test_protocol_version(self):
        self.assertEqual(PROTOCOL_VERSION, '1.0')

    def test_heartbeat_interval(self):
        self.assertEqual(HEARTBEAT_INTERVAL_SECONDS, 30)


class EventTypesTests(SimpleTestCase):

    def test_all_deployment_events_exist(self):
        events = [
            'deployment.queued',
            'deployment.started',
            'deployment.waiting',
            'deployment.completed',
            'deployment.failed',
            'deployment.cancelled',
            'deployment.warning',
            'deployment.info',
            'deployment.cancel_requested',
        ]
        for event in events:
            self.assertIn(event, [e.value for e in EventTypes])

    def test_stage_events_exist(self):
        self.assertEqual(EventTypes.STAGE_STARTED.value, 'stage.started')
        self.assertEqual(EventTypes.STAGE_COMPLETED.value, 'stage.completed')
        self.assertEqual(EventTypes.PROGRESS_UPDATED.value, 'progress.updated')

    def test_system_events_exist(self):
        self.assertEqual(EventTypes.SYSTEM_NOTIFICATION.value, 'system.notification')
        self.assertEqual(EventTypes.CONNECTION_ESTABLISHED.value, 'connection.established')
        self.assertEqual(EventTypes.ACTION_ACKNOWLEDGED.value, 'action.acknowledged')
        self.assertEqual(EventTypes.HEARTBEAT_PONG.value, 'pong')
        self.assertEqual(EventTypes.ERROR.value, 'error')

    def test_event_types_are_strings(self):
        for et in EventTypes:
            self.assertIsInstance(et.value, str)


class ClientActionsTests(SimpleTestCase):

    def test_actions_exist(self):
        self.assertEqual(ClientActions.PING.value, 'ping')
        self.assertEqual(ClientActions.SUBSCRIBE_DEPLOYMENT.value, 'subscribe.deployment')
        self.assertEqual(ClientActions.CANCEL_DEPLOYMENT.value, 'cancel.deployment')


class CloseCodesTests(SimpleTestCase):

    def test_auth_codes(self):
        self.assertEqual(CloseCodes.AUTH_FAILED.value, 4001)
        self.assertEqual(CloseCodes.AUTH_EXPIRED.value, 4002)
        self.assertEqual(CloseCodes.NOT_AUTHORIZED.value, 4003)
