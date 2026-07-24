import logging
import smtplib
from email.message import EmailMessage
from typing import Any, Dict, List, Optional

from .base import BaseNotificationService
from ....exceptions import DevopsException


class EmailNotificationService(BaseNotificationService):
    """Email notification implementation."""

    provider_name = 'email'

    supported_channels = ['email']

    def __init__(self, smtp_host: str = 'localhost', smtp_port: int = 25, username: Optional[str] = None, password: Optional[str] = None) -> None:
        super().__init__()
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.logger = logging.getLogger(self.__class__.__name__)

    def _deliver(self, subject: str, message: str, recipients: List[str], metadata: Optional[Dict[str, Any]] = None) -> None:
        email = EmailMessage()
        email['Subject'] = subject
        email['To'] = ', '.join(recipients)
        email['From'] = metadata.get('from', 'noreply@example.com') if metadata else 'noreply@example.com'
        email.set_content(message)
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as client:
                if self.username and self.password:
                    client.login(self.username, self.password)
                client.send_message(email)
        except Exception as exc:
            self.logger.error('Email delivering failed: %s', exc)
            raise DevopsException(str(exc)) from exc
        self.logger.info('Sent email notification to %s', recipients)
