"""Reusable workflow step definition."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional

from .execution_state import StepExecutionRecord, StepState
from .exceptions import StepExecutionException

logger = logging.getLogger(__name__)


class RetryPolicy:
    def __init__(self, max_attempts: int = 1, backoff_seconds: int = 0) -> None:
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds


@dataclass
class WorkflowStep:
    step_id: str
    name: str
    action: Callable[['ExecutionContext'], Dict[str, Any]]
    rollback_action: Optional[Callable[['ExecutionContext'], None]] = None
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def execute(self, context: 'ExecutionContext') -> StepExecutionRecord:
        record = StepExecutionRecord(step_id=self.step_id, name=self.name)
        record.started_at = datetime.utcnow()
        record.state = StepState.RUNNING
        record.attempts += 1
        logger.info('Starting workflow step %s', self.step_id)

        try:
            result = self.action(context)
            record.result = result
            record.state = StepState.SUCCEEDED
            logger.info('Completed workflow step %s', self.step_id)
        except Exception as exc:
            record.error = str(exc)
            record.state = StepState.FAILED
            logger.error('Workflow step %s failed: %s', self.step_id, exc)
            raise StepExecutionException(self.step_id, f'Step failed: {exc}') from exc
        finally:
            record.finished_at = datetime.utcnow()

        return record

    def rollback(self, context: 'ExecutionContext') -> None:
        if not self.rollback_action:
            return
        logger.info('Rolling back workflow step %s', self.step_id)
        try:
            self.rollback_action(context)
        except Exception as exc:
            logger.error('Rollback failed for step %s: %s', self.step_id, exc)
            raise StepExecutionException(self.step_id, f'Rollback failed: {exc}') from exc
