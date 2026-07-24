from abc import abstractmethod
from typing import Any, Dict, List, Optional

from .base import ServiceInterface
from ...exceptions import PipelineException


class PipelineInterface(ServiceInterface):
    """Abstract contract for pipeline lifecycle management.

    Responsibilities:
        - Create, execute, suspend, and monitor pipelines.
    Excluded responsibilities:
        - Pipeline engine implementation details.
    """

    @abstractmethod
    def create_pipeline(self, definition: Dict[str, Any]) -> str:
        """Create a pipeline and return its identifier."""
        raise PipelineException('create_pipeline not implemented')

    @abstractmethod
    def execute_pipeline(self, pipeline_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a pipeline and return execution metadata."""
        raise PipelineException('execute_pipeline not implemented')

    @abstractmethod
    def suspend_pipeline(self, pipeline_id: str) -> None:
        """Suspend a running pipeline."""
        raise PipelineException('suspend_pipeline not implemented')

    @abstractmethod
    def resume_pipeline(self, pipeline_id: str) -> None:
        """Resume a suspended pipeline."""
        raise PipelineException('resume_pipeline not implemented')

    @abstractmethod
    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Return the current status of the pipeline."""
        raise PipelineException('get_pipeline_status not implemented')

    @abstractmethod
    def list_pipeline_runs(self, pipeline_id: str) -> List[Dict[str, Any]]:
        """List execution runs for a given pipeline."""
        raise PipelineException('list_pipeline_runs not implemented')
