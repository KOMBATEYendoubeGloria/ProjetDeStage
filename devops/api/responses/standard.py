"""Standard API response helper for consistent REST responses."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from rest_framework.response import Response


class StandardResponse:
    """Unified response format for all DevOps API endpoints.

    Every response follows::

        {
            "success": true,
            "message": "...",
            "data": {},
            "errors": [],
            "timestamp": "...",
            "request_id": "..."
        }
    """

    @staticmethod
    def _build_payload(
        success: bool,
        message: str,
        data: Any = None,
        errors: Optional[List[str]] = None,
        status_code: int = 200,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            'success': success,
            'message': message,
            'data': data if data is not None else {},
            'errors': errors if errors is not None else [],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'request_id': request_id or str(uuid.uuid4()),
        }

    @classmethod
    def success(
        cls,
        data: Any = None,
        message: str = 'Success',
        status_code: int = 200,
        request_id: Optional[str] = None,
    ) -> Response:
        payload = cls._build_payload(
            success=True,
            message=message,
            data=data,
            status_code=status_code,
            request_id=request_id,
        )
        return Response(payload, status=status_code)

    @classmethod
    def error(
        cls,
        errors: List[str],
        message: str = 'An error occurred',
        status_code: int = 400,
        request_id: Optional[str] = None,
    ) -> Response:
        payload = cls._build_payload(
            success=False,
            message=message,
            errors=errors,
            status_code=status_code,
            request_id=request_id,
        )
        return Response(payload, status=status_code)
