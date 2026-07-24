from django.test import SimpleTestCase
from devops.services.implementations.logging.default import DefaultLoggingService
from devops.services.implementations.monitoring.default import DefaultMonitoringService
from devops.services.implementations.notification.email import EmailNotificationService
from devops.services.implementations.notification.webhook import WebhookNotificationService
from unittest.mock import Mock, patch


class MonitoringServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = DefaultMonitoringService()
        self.service.metrics = {
            'cpu': {'target_id': 'vm1', 'value': 50},
        }
        self.service.events = [
            {'target_id': 'vm1', 'severity': 'warning', 'message': 'high cpu'},
        ]

    def test_get_metrics(self):
        metrics = self.service.get_metrics(target_id='vm1')
        self.assertIn('cpu', metrics)

    def test_get_status(self):
        status = self.service.get_status(target_id='vm1')
        self.assertTrue(status['healthy'])

    def test_get_alerts(self):
        alerts = self.service.get_alerts(severity='warning')
        self.assertEqual(len(alerts), 1)

    def test_get_events(self):
        events = self.service.get_events(target_id='vm1', limit=1)
        self.assertEqual(len(events), 1)


class LoggingServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = DefaultLoggingService()

    def test_log_event_and_query(self):
        self.service.log_event({'level': 'info', 'message': 'ok'})
        entries = self.service.query_logs()
        self.assertEqual(len(entries), 1)

    def test_log_summary_counts_levels(self):
        self.service.log_event({'level': 'warning'})
        summary = self.service.get_log_summary()
        self.assertEqual(summary['count'], 1)
        self.assertEqual(summary['levels']['warning'], 1)


class NotificationServiceTests(SimpleTestCase):
    @patch('devops.services.implementations.notification.email.smtplib.SMTP')
    def test_send_email_notification(self, smtp_mock):
        service = EmailNotificationService(smtp_host='localhost', smtp_port=25)
        service.send_notification('Hello', 'Message', ['user@example.com'], metadata={'from': 'test@example.com'})
        smtp_mock.assert_called_once()

    @patch('urllib.request.urlopen')
    def test_send_webhook_notification(self, urlopen_mock):
        mock_response = Mock()
        mock_response.status = 200
        urlopen_mock.return_value.__enter__.return_value = mock_response
        service = WebhookNotificationService(timeout=5)
        service.send_notification('Hello', 'Message', ['http://example.com/webhook'])
        self.assertEqual(service.list_channels(), [{'name': 'webhook'}])
