"""Tests for EventBus."""

from django.test import SimpleTestCase

from devops.deployment.events.event_bus import EventBus


class EventBusTests(SimpleTestCase):

    def test_subscribe_and_publish(self):
        bus = EventBus()
        received = []
        bus.subscribe('test', lambda t, p: received.append((t, p)))
        bus.publish('test', {'key': 'value'})
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0], ('test', {'key': 'value'}))

    def test_multiple_subscribers(self):
        bus = EventBus()
        r1, r2 = [], []
        bus.subscribe('ev', lambda t, p: r1.append(p))
        bus.subscribe('ev', lambda t, p: r2.append(p))
        bus.publish('ev', {'a': 1})
        self.assertEqual(r1, [{'a': 1}])
        self.assertEqual(r2, [{'a': 1}])

    def test_unsubscribe(self):
        bus = EventBus()
        received = []
        callback = lambda t, p: received.append(p)
        bus.subscribe('ev', callback)
        bus.unsubscribe('ev', callback)
        bus.publish('ev', {})
        self.assertEqual(received, [])

    def test_publish_no_subscribers(self):
        bus = EventBus()
        bus.publish('nonexistent', {})  # should not raise

    def test_clear(self):
        bus = EventBus()
        bus.subscribe('ev', lambda t, p: None)
        bus.clear()
        self.assertEqual(bus._subscribers, {})

    def test_subscriber_error_does_not_propagate(self):
        bus = EventBus()

        def bad_callback(t, p):
            raise RuntimeError('boom')

        bus.subscribe('ev', bad_callback)
        bus.publish('ev', {})  # should not raise

    def test_different_event_types(self):
        bus = EventBus()
        r_a, r_b = [], []
        bus.subscribe('a', lambda t, p: r_a.append(p))
        bus.subscribe('b', lambda t, p: r_b.append(p))
        bus.publish('a', {'from': 'a'})
        bus.publish('b', {'from': 'b'})
        self.assertEqual(r_a, [{'from': 'a'}])
        self.assertEqual(r_b, [{'from': 'b'}])
