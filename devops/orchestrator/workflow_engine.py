"""Workflow execution engine for deployment orchestration."""

from __future__ import annotations

import logging
from typing import Callable, Dict, Optional

from .execution_context import ExecutionContext
from .execution_state import WorkflowExecutionRecord, WorkflowState, StepExecutionRecord, StepState
from .exceptions import WorkflowException, StepExecutionException
from .events import (
    WorkflowStarted,
    StepStarted,
    StepCompleted,
    StepFailed,
    WorkflowCompleted,
    WorkflowFailed,
    RollbackStarted,
    RollbackCompleted,
)
from .event_dispatcher import EventDispatcher
from .rollback_manager import RollbackManager
from .step import WorkflowStep
from .workflow import WorkflowDefinition, Workflow

logger = logging.getLogger(__name__)


def _safe_dispatch(dispatcher: EventDispatcher, event_name: str, event: object) -> None:
    try:
        dispatcher.dispatch(event_name, event)
    except Exception as exc:
        logger.warning('Event listener failed for %s: %s', event_name, exc)


class WorkflowEngine:
    def __init__(self, dispatcher: Optional[EventDispatcher] = None, rollback_manager: Optional[RollbackManager] = None) -> None:
        self.dispatcher = dispatcher or EventDispatcher()
        self.rollback_manager = rollback_manager or RollbackManager()

    def run(self, workflow_definition: WorkflowDefinition, context: ExecutionContext) -> WorkflowExecutionRecord:
        workflow = Workflow.create(workflow_definition)
        workflow.record.state = WorkflowState.RUNNING
        workflow.record.started_at = __import__('datetime').datetime.utcnow()
        _safe_dispatch(self.dispatcher, 'workflow_started', WorkflowStarted(workflow_id=workflow.record.workflow_id, name=workflow.record.name, context=context.__dict__))

        for step, step_record in zip(workflow.definition.steps, workflow.record.steps):
            step_record.state = StepState.RUNNING
            step_record.started_at = __import__('datetime').datetime.utcnow()
            _safe_dispatch(self.dispatcher, 'step_started', StepStarted(workflow_id=workflow.record.workflow_id, step_id=step.step_id, step_name=step.name, context=context.__dict__))

            try:
                result_record = step.execute(context)
                step_record.state = result_record.state
                step_record.result = result_record.result
                step_record.error = result_record.error
                step_record.finished_at = result_record.finished_at
                step_record.attempts = result_record.attempts
                step_record.logs.extend(result_record.logs)
                _safe_dispatch(self.dispatcher, 'step_completed', StepCompleted(workflow_id=workflow.record.workflow_id, step_id=step.step_id, step_name=step.name, result=result_record.result or {}))
            except StepExecutionException as exc:
                step_record.state = StepState.FAILED
                step_record.error = str(exc)
                context.record_error({'step_id': step.step_id, 'error': str(exc)})
                _safe_dispatch(self.dispatcher, 'step_failed', StepFailed(workflow_id=workflow.record.workflow_id, step_id=step.step_id, step_name=step.name, error=str(exc)))
                workflow.record.state = WorkflowState.FAILED

                try:
                    _safe_dispatch(self.dispatcher, 'rollback_started', RollbackStarted(workflow_id=workflow.record.workflow_id, name=workflow.record.name, reason=str(exc)))
                    self.rollback_manager.rollback(workflow.record, context)
                    workflow.record.state = WorkflowState.ROLLED_BACK
                    workflow.record.finished_at = __import__('datetime').datetime.utcnow()
                    _safe_dispatch(self.dispatcher, 'rollback_completed', RollbackCompleted(workflow_id=workflow.record.workflow_id, name=workflow.record.name, result={'status': 'rolled_back'}))
                except Exception as rollback_exc:
                    logger.error('Rollback failed for workflow %s: %s', workflow.record.workflow_id, rollback_exc)
                    raise WorkflowException(f'Rollback failed: {rollback_exc}') from rollback_exc

                raise WorkflowException(f'Workflow failed on step {step.step_id}') from exc

        workflow.record.state = WorkflowState.COMPLETED
        workflow.record.finished_at = __import__('datetime').datetime.utcnow()
        _safe_dispatch(self.dispatcher, 'workflow_completed', WorkflowCompleted(workflow_id=workflow.record.workflow_id, name=workflow.record.name, result={'status': 'completed'}))
        return workflow.record

    def resume(self, workflow_definition: WorkflowDefinition, workflow_record: WorkflowExecutionRecord, context: ExecutionContext) -> WorkflowExecutionRecord:
        if workflow_record.state != WorkflowState.FAILED:
            raise WorkflowException('Only failed workflows can be resumed')

        workflow_record.state = WorkflowState.RUNNING
        workflow_record.errors.clear()
        _safe_dispatch(self.dispatcher, 'workflow_started', WorkflowStarted(workflow_id=workflow_record.workflow_id, name=workflow_record.name, context=context.__dict__))

        failed = False
        for step, step_record in zip(workflow_definition.steps, workflow_record.steps):
            if step_record.state == StepState.SUCCEEDED:
                continue
            if step_record.state == StepState.FAILED:
                failed = True
            if not failed and step_record.state == StepState.PENDING:
                continue

            step_record.state = StepState.RUNNING
            step_record.started_at = __import__('datetime').datetime.utcnow()
            _safe_dispatch(self.dispatcher, 'step_started', StepStarted(workflow_id=workflow_record.workflow_id, step_id=step.step_id, step_name=step.name, context=context.__dict__))

            try:
                result_record = step.execute(context)
                step_record.state = result_record.state
                step_record.result = result_record.result
                step_record.error = result_record.error
                step_record.finished_at = result_record.finished_at
                step_record.attempts = result_record.attempts
                step_record.logs.extend(result_record.logs)
                _safe_dispatch(self.dispatcher, 'step_completed', StepCompleted(workflow_id=workflow_record.workflow_id, step_id=step.step_id, step_name=step.name, result=result_record.result or {}))
            except StepExecutionException as exc:
                step_record.state = StepState.FAILED
                step_record.error = str(exc)
                context.record_error({'step_id': step.step_id, 'error': str(exc)})
                _safe_dispatch(self.dispatcher, 'step_failed', StepFailed(workflow_id=workflow_record.workflow_id, step_id=step.step_id, step_name=step.name, error=str(exc)))
                workflow_record.state = WorkflowState.FAILED

                try:
                    _safe_dispatch(self.dispatcher, 'rollback_started', RollbackStarted(workflow_id=workflow_record.workflow_id, name=workflow_record.name, reason=str(exc)))
                    self.rollback_manager.rollback(workflow_record, context)
                    workflow_record.state = WorkflowState.ROLLED_BACK
                    workflow_record.finished_at = __import__('datetime').datetime.utcnow()
                    _safe_dispatch(self.dispatcher, 'rollback_completed', RollbackCompleted(workflow_id=workflow_record.workflow_id, name=workflow_record.name, result={'status': 'rolled_back'}))
                except Exception as rollback_exc:
                    logger.error('Rollback failed for workflow %s: %s', workflow_record.workflow_id, rollback_exc)
                    raise WorkflowException(f'Rollback failed: {rollback_exc}') from rollback_exc

                raise WorkflowException(f'Workflow failed on step {step.step_id}') from exc

        workflow_record.state = WorkflowState.COMPLETED
        workflow_record.finished_at = __import__('datetime').datetime.utcnow()
        _safe_dispatch(self.dispatcher, 'workflow_completed', WorkflowCompleted(workflow_id=workflow_record.workflow_id, name=workflow_record.name, result={'status': 'completed'}))
        return workflow_record
