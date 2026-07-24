"""Rollback strategy manager for orchestration."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from .execution_state import WorkflowExecutionRecord, StepState, WorkflowState
from .exceptions import RollbackException

logger = logging.getLogger(__name__)


class RollbackManager:
    def rollback(self, workflow_record: WorkflowExecutionRecord, context: 'ExecutionContext') -> Dict[str, Any]:
        logger.info('Starting rollback for workflow %s', workflow_record.workflow_id)
        workflow_record.state = WorkflowState.ROLLING_BACK
        errors: List[Dict[str, Any]] = []

        for step_record in reversed(workflow_record.steps):
            if step_record.state != StepState.SUCCEEDED:
                continue
            try:
                rollback_action = context.metadata.get('rollbackable_steps', {}).get(step_record.step_id)
                if rollback_action:
                    rollback_action(context)
                step_record.state = StepState.ROLLED_BACK
                logger.info('Rolled back step %s', step_record.step_id)
            except Exception as exc:
                error_payload = {'step_id': step_record.step_id, 'error': str(exc)}
                errors.append(error_payload)
                logger.error('Rollback error for step %s: %s', step_record.step_id, exc)

        if errors:
            workflow_record.state = WorkflowState.FAILED
            raise RollbackException(f'Rollback completed with errors: {errors}')

        workflow_record.state = WorkflowState.ROLLED_BACK
        logger.info('Rollback completed for workflow %s', workflow_record.workflow_id)
        return {'status': 'rolled_back'}
