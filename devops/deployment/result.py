"""Data structure encapsulating the result of a deployment run."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class DeploymentResult:
    """Structured outcome of a deployment orchestration run."""

    status: str = 'PENDING'
    provider: str = ''
    deployment_id: str = ''
    logs: List[str] = field(default_factory=list)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None
    outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def mark_started(self) -> None:
        """Record the deployment start timestamp."""
        self.start_time = datetime.now(timezone.utc).isoformat()

    def mark_completed(self) -> None:
        """Record the deployment end timestamp and compute duration."""
        self.end_time = datetime.now(timezone.utc).isoformat()
        self.status = 'SUCCESS'
        if self.start_time:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            self.duration = (end - start).total_seconds()

    def mark_failed(self, error: str) -> None:
        """Record the deployment failure."""
        self.end_time = datetime.now(timezone.utc).isoformat()
        self.status = 'FAILED'
        self.errors.append(error)
        if self.start_time:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            self.duration = (end - start).total_seconds()

    def add_log(self, message: str) -> None:
        """Append a timestamped log entry."""
        timestamp = datetime.now(timezone.utc).strftime('%H:%M:%S')
        self.logs.append(f'[{timestamp}] {message}')

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)
