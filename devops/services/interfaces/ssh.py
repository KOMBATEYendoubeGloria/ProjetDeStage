from abc import abstractmethod
from typing import Any, Dict, Optional

from .base import ServiceInterface
from ...exceptions import SSHException


class SSHInterface(ServiceInterface):
    """Abstract contract for SSH connectivity and remote command execution.

    Responsibilities:
        - Provide generic SSH session and execution primitives.
    Excluded responsibilities:
        - Transport-specific implementation details.
    """

    @abstractmethod
    def connect(self, host: str, port: int = 22, username: Optional[str] = None, key: Optional[str] = None, password: Optional[str] = None, timeout: Optional[int] = None) -> None:
        """Establish an SSH connection to a remote host."""
        raise SSHException('connect not implemented')

    @abstractmethod
    def execute(self, command: str, timeout: Optional[int] = None, environment: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute a command on the remote host."""
        raise SSHException('execute not implemented')

    @abstractmethod
    def copy(self, local_path: str, remote_path: str) -> None:
        """Copy a file to the remote host."""
        raise SSHException('copy not implemented')

    @abstractmethod
    def close(self) -> None:
        """Close the SSH session."""
        raise SSHException('close not implemented')
