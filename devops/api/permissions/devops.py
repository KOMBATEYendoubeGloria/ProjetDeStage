"""DevOps API permissions."""

from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsDevopsUser(BasePermission):
    """Allow access only to authenticated DevOps users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
