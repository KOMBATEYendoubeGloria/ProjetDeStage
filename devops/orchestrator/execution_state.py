"""Workflow and step state definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class StepState(str, Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    SKIPPED = 'skipped'
    ROLLED_BACK = 'rolled_back'


class WorkflowState(str, Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    ROLLING_BACK = 'rolling_back'
    ROLLED_BACK = 'rolled_back'


@dataclass
class StepExecutionRecord:
    step_id: str
    name: str
    state: StepState = StepState.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    attempts: int = 0
    logs: list[str] = field(default_factory=list)

    def duration(self) -> Optional[float]:
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None


@dataclass
class WorkflowExecutionRecord:
    workflow_id: str
    name: str
    state: WorkflowState = WorkflowState.PENDING
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    steps: list[StepExecutionRecord] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: list[Dict[str, Any]] = field(default_factory=list)

    def progress(self) -> float:
        if not self.steps:
            return 0.0
        completed = sum(1 for step in self.steps if step.state in (StepState.SUCCEEDED, StepState.SKIPPED, StepState.ROLLED_BACK))
        return round((completed / len(self.steps)) * 100.0, 2)
