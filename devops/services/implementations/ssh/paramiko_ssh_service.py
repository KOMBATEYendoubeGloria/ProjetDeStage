from .base import BaseSSHService


class ParamikoSSHService(BaseSSHService):
    """Paramiko SSH service implementation."""

    provider_name = 'paramiko'

    def __init__(self) -> None:
        super().__init__()
