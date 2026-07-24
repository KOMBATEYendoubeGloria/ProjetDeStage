"""Validation helper for centralized configuration payloads."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ...exceptions import ValidationException

logger = logging.getLogger(__name__)

try:
    import jsonschema  # type: ignore[import]
except ImportError:  # pragma: no cover
    jsonschema = None


def _resolve_expected_type(type_name: str) -> Any:
    mapping = {
        'string': str,
        'integer': int,
        'number': (int, float),
        'boolean': bool,
        'object': dict,
        'array': list,
    }
    return mapping.get(type_name, object)


class ValidationManager:
    """Validate configuration payloads and provider schemas."""

    def validate(self, payload: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not isinstance(payload, dict):
            raise ValidationException('Validation payload must be a dict')

        if schema is None:
            logger.debug('No validation schema supplied; skipping schema validation')
            return []

        if jsonschema is not None:
            try:
                jsonschema.validate(payload, schema)
                return []
            except Exception as exc:
                raise ValidationException(f'Payload failed schema validation: {exc}') from exc

        if not isinstance(schema, dict):
            raise ValidationException('Validation schema must be a dict')

        issues: List[Dict[str, Any]] = []

        required = schema.get('required', [])
        if isinstance(required, list):
            for field in required:
                if field not in payload:
                    issues.append({'field': field, 'message': 'missing required field'})

        properties = schema.get('properties', {})
        if isinstance(properties, dict):
            for field, rules in properties.items():
                if field not in payload:
                    continue
                if not isinstance(rules, dict):
                    continue
                expected_type = rules.get('type')
                if expected_type:
                    expected = _resolve_expected_type(expected_type)
                    if not isinstance(payload[field], expected):
                        issues.append({
                            'field': field,
                            'message': f'expected type {expected_type}',
                        })

        if issues:
            raise ValidationException(f'Payload failed validation: {issues}')

        logger.debug('Payload passed validation against schema')
        return issues
