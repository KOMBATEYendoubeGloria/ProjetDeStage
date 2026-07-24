from abc import abstractmethod
from typing import Any, Dict, List, Optional

from .base import ServiceInterface
from ...exceptions import ContainerException


class ContainerInterface(ServiceInterface):
    """Abstract contract for container engine operations.

    Responsibilities:
        - Manage containers and images in a provider-agnostic way.
    Excluded responsibilities:
        - Provider-specific orchestration details.
    """

    @abstractmethod
    def list_containers(self, all_containers: bool = False) -> List[Dict[str, Any]]:
        """List containers available on the host."""
        raise ContainerException('list_containers not implemented')

    @abstractmethod
    def get_container(self, container_id: str) -> Dict[str, Any]:
        """Get metadata for a specific container."""
        raise ContainerException('get_container not implemented')

    @abstractmethod
    def create_container(self, image: str, name: Optional[str] = None, command: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> str:
        """Create a new container and return its identifier."""
        raise ContainerException('create_container not implemented')

    @abstractmethod
    def start_container(self, container_id: str) -> None:
        """Start a previously created container."""
        raise ContainerException('start_container not implemented')

    @abstractmethod
    def stop_container(self, container_id: str) -> None:
        """Stop a running container."""
        raise ContainerException('stop_container not implemented')

    @abstractmethod
    def remove_container(self, container_id: str, force: bool = False) -> None:
        """Remove a container from the host."""
        raise ContainerException('remove_container not implemented')

    @abstractmethod
    def list_images(self) -> List[Dict[str, Any]]:
        """List available container images."""
        raise ContainerException('list_images not implemented')

    @abstractmethod
    def pull_image(self, image: str) -> str:
        """Pull an image from a registry and return its canonical name."""
        raise ContainerException('pull_image not implemented')
