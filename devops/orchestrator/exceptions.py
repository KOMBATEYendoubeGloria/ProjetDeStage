"""Exceptions raised by the deployment orchestrator."""

from __future__ import annotations

from typing import Any, Dict, Optional


class WorkflowException(Exception):
    """Raised when a workflow cannot execute."""


class StepExecutionException(WorkflowException):
    """Raised when an individual workflow step fails."""

    def __init__(self, step_id: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.step_id = step_id
        self.details = details or {}


class RollbackException(WorkflowException):
    """Raised when rollback cannot complete."""


class ResumeException(WorkflowException):
    """Raised when workflow resume fails."""
