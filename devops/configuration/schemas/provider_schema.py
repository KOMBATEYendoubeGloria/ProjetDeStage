"""Provider schema registry for centralized configuration validation."""

from __future__ import annotations

from typing import Any, Dict, Optional


class ProviderSchema:
    """Registry for provider-specific configuration schemas."""

    _schemas: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register_schema(cls, provider_name: str, schema: Dict[str, Any]) -> None:
        if not isinstance(schema, dict):
            raise TypeError('Provider schema must be a dict')
        cls._schemas[provider_name.strip().lower()] = schema

    @classmethod
    def get_schema(cls, provider_name: str) -> Optional[Dict[str, Any]]:
        return cls._schemas.get(provider_name.strip().lower())

    @classmethod
    def available_schemas(cls) -> list[str]:
        return sorted(cls._schemas.keys())
