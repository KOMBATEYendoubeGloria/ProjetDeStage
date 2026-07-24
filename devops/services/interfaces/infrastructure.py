from abc import abstractmethod
from typing import Any, Dict, Optional

from .base import ServiceInterface
from ...exceptions import InfrastructureException


class InfrastructureInterface(ServiceInterface):
    """Abstract contract for infrastructure management tools.

    Responsibilities:
        - Manage lifecycle of infrastructure definitions.
        - Provide provider-agnostic infrastructure actions.
    Excluded responsibilities:
        - Resource-specific lower-level networking and compute APIs.
    """

    @abstractmethod
    def init(self, workspace_path: str, backend_config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize infrastructure tooling in a workspace."""
        raise InfrastructureException('init not implemented')

    @abstractmethod
    def validate(self, workspace_path: str) -> None:
        """Validate the current infrastructure configuration."""
        raise InfrastructureException('validate not implemented')

    @abstractmethod
    def plan(self, workspace_path: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate an execution plan for the infrastructure."""
        raise InfrastructureException('plan not implemented')

    @abstractmethod
    def apply(self, workspace_path: str, variables: Optional[Dict[str, Any]] = None, auto_approve: bool = False) -> Dict[str, Any]:
        """Apply infrastructure changes."""
        raise InfrastructureException('apply not implemented')

    @abstractmethod
    def destroy(self, workspace_path: str, variables: Optional[Dict[str, Any]] = None, auto_approve: bool = False) -> Dict[str, Any]:
        """Destroy managed infrastructure."""
        raise InfrastructureException('destroy not implemented')

    @abstractmethod
    def output(self, workspace_path: str) -> Dict[str, Any]:
        """Read outputs produced by the infrastructure tooling."""
        raise InfrastructureException('output not implemented')

    @abstractmethod
    def workspace(self, workspace_path: str, name: str) -> None:
        """Select or create an infrastructure workspace."""
        raise InfrastructureException('workspace not implemented')
