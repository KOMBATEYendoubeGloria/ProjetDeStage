from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Autorise uniquement les utilisateurs avec le rôle Admin"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsAdminOrSelf(BasePermission):
    """Autorise un Admin sur tout, ou un utilisateur sur son propre profil"""
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'ADMIN' or obj == request.user