"""High-level orchestrator interface for deployment workflows."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..services import ServiceContainer
from .execution_context import ExecutionContext
from .events import WorkflowFailed
from .exceptions import WorkflowException, ResumeException
from .event_dispatcher import EventDispatcher
from .execution_state import WorkflowExecutionRecord, WorkflowState
from .rollback_manager import RollbackManager
from .workflow import WorkflowDefinition
from .workflow_engine import WorkflowEngine

logger = logging.getLogger(__name__)


class DeploymentOrchestrator:
    def __init__(self, dispatcher: Optional[EventDispatcher] = None) -> None:
        self.dispatcher = dispatcher or EventDispatcher()
        self.engine = WorkflowEngine(dispatcher=self.dispatcher, rollback_manager=RollbackManager())
        self.container = ServiceContainer()

    def execute(self, workflow_definition: WorkflowDefinition, context: ExecutionContext) -> Dict[str, Any]:
        try:
            record = self.engine.run(workflow_definition, context)
            logger.info('Workflow %s completed successfully', workflow_definition.workflow_id)
            return {'workflow_id': record.workflow_id, 'state': record.state, 'progress': record.progress(), 'outputs': context.outputs}
        except WorkflowException as exc:
            logger.error('Workflow %s failed: %s', workflow_definition.workflow_id, exc)
            self.dispatcher.dispatch('workflow_failed', WorkflowFailed(workflow_id=workflow_definition.workflow_id, name=workflow_definition.name, error=str(exc)))
            raise

    def rollback(self, workflow_record: 'WorkflowExecutionRecord', context: ExecutionContext) -> Dict[str, Any]:
        return self.engine.rollback_manager.rollback(workflow_record, context)

    def resume(self, workflow_definition: WorkflowDefinition, workflow_record: WorkflowExecutionRecord, context: ExecutionContext) -> Dict[str, Any]:
        if workflow_record.state != WorkflowState.FAILED:
            raise ResumeException('Only failed workflows can be resumed')

        record = self.engine.resume(workflow_definition, workflow_record, context)
        return {'workflow_id': record.workflow_id, 'state': record.state, 'progress': record.progress(), 'outputs': context.outputs}

    def resolve_service(self, interface: Any, provider_name: Optional[str] = None, config: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Any:
        return self.container.resolve(interface, provider_name=provider_name, config=config, **kwargs)
