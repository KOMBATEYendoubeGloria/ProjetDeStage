"""Workflow definitions for the deployment orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .execution_state import StepExecutionRecord, WorkflowExecutionRecord
from .step import WorkflowStep


@dataclass
class WorkflowDefinition:
    workflow_id: str
    name: str
    steps: List[WorkflowStep]
    description: str = ''
    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            'workflow_id': self.workflow_id,
            'name': self.name,
            'description': self.description,
            'steps': [step.step_id for step in self.steps],
            'metadata': self.metadata,
        }


@dataclass
class Workflow:
    definition: WorkflowDefinition
    record: WorkflowExecutionRecord

    @classmethod
    def create(cls, definition: WorkflowDefinition) -> 'Workflow':
        record = WorkflowExecutionRecord(
            workflow_id=definition.workflow_id,
            name=definition.name,
            metadata=definition.metadata.copy(),
        )
        record.steps = [StepExecutionRecord(step_id=step.step_id, name=step.name) for step in definition.steps]
        return cls(definition=definition, record=record)
