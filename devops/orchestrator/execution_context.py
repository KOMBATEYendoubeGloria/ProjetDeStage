"""Execution context shared across workflow steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ExecutionContext:
    workflow_id: str
    user_id: Optional[str]
    project_id: Optional[str]
    environment: Optional[str]
    provider_name: Optional[str]
    variables: Dict[str, Any] = field(default_factory=dict)
    secrets: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    errors: list[Dict[str, Any]] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)

    def record_output(self, key: str, value: Any) -> None:
        self.outputs[key] = value

    def record_error(self, error: Dict[str, Any]) -> None:
        self.errors.append(error)

    def record_log(self, message: str) -> None:
        self.logs.append(message)
