"""Registry for reusable workflow steps."""

from __future__ import annotations

from typing import Dict, Optional

from .step import WorkflowStep


class StepRegistry:
    def __init__(self) -> None:
        self._steps: Dict[str, WorkflowStep] = {}

    def register(self, step: WorkflowStep) -> None:
        self._steps[step.step_id] = step

    def get(self, step_id: str) -> Optional[WorkflowStep]:
        return self._steps.get(step_id)

    def list_steps(self) -> list[str]:
        return list(self._steps.keys())
