"""Track workflow execution progress."""

from __future__ import annotations

from typing import Optional

from .execution_state import WorkflowExecutionRecord, StepState


class ProgressTracker:
    def __init__(self, record: WorkflowExecutionRecord) -> None:
        self.record = record

    def current_step(self) -> Optional[str]:
        for step in self.record.steps:
            if step.state == StepState.RUNNING:
                return step.step_id
        return None

    def completed_steps(self) -> list[str]:
        return [step.step_id for step in self.record.steps if step.state == StepState.SUCCEEDED]

    def remaining_steps(self) -> list[str]:
        return [step.step_id for step in self.record.steps if step.state in (StepState.PENDING, StepState.FAILED)]

    def progress(self) -> float:
        return self.record.progress()
