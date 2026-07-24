"""Environment profile representation for configuration engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class EnvironmentProfile:
    name: str
    environment: str
    values: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'environment': self.environment,
            'values': self.values,
        }
