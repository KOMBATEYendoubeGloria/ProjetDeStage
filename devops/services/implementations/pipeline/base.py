import logging
from typing import Any, Dict, List, Optional

from ....exceptions import PipelineException
from ...interfaces.pipeline import PipelineInterface


class BasePipelineService(PipelineInterface):
    """Base pipeline service implementation."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pipelines: Dict[str, Dict[str, Any]] = {}
        self.pipeline_runs: Dict[str, List[Dict[str, Any]]] = {}

    def create_pipeline(self, definition: Dict[str, Any]) -> str:
        pipeline_id = definition.get('id') or definition.get('name')
        if not pipeline_id:
            raise PipelineException('Pipeline definition requires an id or name')
        self.pipelines[pipeline_id] = definition
        self.pipeline_runs[pipeline_id] = []
        self.logger.info('Created pipeline %s', pipeline_id)
        return pipeline_id

    def execute_pipeline(self, pipeline_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if pipeline_id not in self.pipelines:
            raise PipelineException('Pipeline not found')
        run = {
            'id': f'{pipeline_id}-{len(self.pipeline_runs[pipeline_id]) + 1}',
            'pipeline_id': pipeline_id,
            'parameters': parameters or {},
            'status': 'succeeded',
        }
        self.pipeline_runs[pipeline_id].append(run)
        self.logger.info('Executed pipeline %s', pipeline_id)
        return run

    def suspend_pipeline(self, pipeline_id: str) -> None:
        if pipeline_id not in self.pipelines:
            raise PipelineException('Pipeline not found')
        self.logger.info('Suspended pipeline %s', pipeline_id)

    def resume_pipeline(self, pipeline_id: str) -> None:
        if pipeline_id not in self.pipelines:
            raise PipelineException('Pipeline not found')
        self.logger.info('Resumed pipeline %s', pipeline_id)

    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        if pipeline_id not in self.pipelines:
            raise PipelineException('Pipeline not found')
        status = {
            'pipeline_id': pipeline_id,
            'runs': self.pipeline_runs[pipeline_id],
        }
        self.logger.info('Retrieved status for pipeline %s', pipeline_id)
        return status

    def list_pipeline_runs(self, pipeline_id: str) -> List[Dict[str, Any]]:
        if pipeline_id not in self.pipelines:
            raise PipelineException('Pipeline not found')
        return self.pipeline_runs[pipeline_id]
