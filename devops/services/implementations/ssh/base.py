import logging
from typing import Any, Dict, Optional

from ....exceptions import SSHException
from ...interfaces.ssh import SSHInterface

try:
    import paramiko
except ImportError:  # pragma: no cover
    paramiko = None


class BaseSSHService(SSHInterface):
    """Base SSH service implementation using Paramiko."""

    def __init__(self) -> None:
        if paramiko is None:
            raise SSHException('paramiko is required for SSH services')
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def connect(self, host: str, port: int = 22, username: Optional[str] = None, key: Optional[str] = None, password: Optional[str] = None, timeout: Optional[int] = None) -> None:
        connect_kwargs = {'hostname': host, 'port': port, 'username': username, 'timeout': timeout}
        if password:
            connect_kwargs['password'] = password
        if key:
            connect_kwargs['key_filename'] = key
        try:
            self.client.connect(**{k: v for k, v in connect_kwargs.items() if v is not None})
        except Exception as exc:
            self.logger.error('SSH connection failed: %s', exc)
            raise SSHException(str(exc)) from exc
        self.logger.info('Connected to SSH host %s', host)

    def execute(self, command: str, timeout: Optional[int] = None, environment: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout, environment=environment)
            result = {
                'stdout': stdout.read().decode('utf-8', errors='ignore'),
                'stderr': stderr.read().decode('utf-8', errors='ignore'),
                'exit_code': stdout.channel.recv_exit_status(),
            }
        except Exception as exc:
            self.logger.error('SSH command execution failed: %s', exc)
            raise SSHException(str(exc)) from exc
        self.logger.info('Executed SSH command on remote host')
        return result

    def copy(self, local_path: str, remote_path: str) -> None:
        try:
            if self.sftp is None:
                self.sftp = self.client.open_sftp()
            self.sftp.put(local_path, remote_path)
        except Exception as exc:
            self.logger.error('SSH copy failed: %s', exc)
            raise SSHException(str(exc)) from exc
        self.logger.info('Copied %s to %s', local_path, remote_path)

    def close(self) -> None:
        try:
            if self.sftp is not None:
                self.sftp.close()
        finally:
            self.client.close()
            self.logger.info('Closed SSH connection')
