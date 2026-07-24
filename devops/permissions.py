from rest_framework import permissions


class IsDevopsUser(permissions.BasePermission):
    """Placeholder permission for DevOps operations."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
