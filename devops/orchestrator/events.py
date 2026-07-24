"""Events emitted by the orchestrator workflow engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class WorkflowStarted:
    workflow_id: str
    name: str
    context: Dict[str, Any]


@dataclass
class StepStarted:
    workflow_id: str
    step_id: str
    step_name: str
    context: Dict[str, Any]


@dataclass
class StepCompleted:
    workflow_id: str
    step_id: str
    step_name: str
    result: Dict[str, Any]


@dataclass
class StepFailed:
    workflow_id: str
    step_id: str
    step_name: str
    error: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class WorkflowCompleted:
    workflow_id: str
    name: str
    result: Dict[str, Any]


@dataclass
class WorkflowFailed:
    workflow_id: str
    name: str
    error: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class RollbackStarted:
    workflow_id: str
    name: str
    reason: str


@dataclass
class RollbackCompleted:
    workflow_id: str
    name: str
    result: Dict[str, Any]
