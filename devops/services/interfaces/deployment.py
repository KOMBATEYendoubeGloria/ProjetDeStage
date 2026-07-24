from abc import abstractmethod
from typing import Any, Dict, List, Optional

from .base import ServiceInterface
from ...exceptions import DeploymentException


class DeploymentInterface(ServiceInterface):
    """Abstract contract for deployment orchestration.

    Responsibilities:
        - Define the contract for a deployment engine.
        - Orchestrate deployment operations without technology dependencies.
    Excluded responsibilities:
        - Executing provider-specific deployment logic.
    """

    @abstractmethod
    def prepare(self, deployment_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Prepare a deployment pipeline for execution."""
        raise DeploymentException('prepare not implemented')

    @abstractmethod
    def execute(self, deployment_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a deployment and return execution details."""
        raise DeploymentException('execute not implemented')

    @abstractmethod
    def cancel(self, deployment_id: str) -> None:
        """Cancel an ongoing deployment."""
        raise DeploymentException('cancel not implemented')

    @abstractmethod
    def status(self, deployment_id: str) -> Dict[str, Any]:
        """Return the current status of a deployment."""
        raise DeploymentException('status not implemented')

    @abstractmethod
    def list_deployments(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List deployments, optionally filtered by project."""
        raise DeploymentException('list_deployments not implemented')
