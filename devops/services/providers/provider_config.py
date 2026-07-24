"""Provider-specific configuration for service resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ProviderConfig:
    """Configuration attached to a provider implementation."""

    provider_name: str
    settings: Dict[str, Any]
    active: bool = True

    def as_dict(self) -> Dict[str, Any]:
        return dict(self.settings)
