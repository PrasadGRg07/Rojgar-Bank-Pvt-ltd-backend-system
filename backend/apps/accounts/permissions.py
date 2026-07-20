from rest_framework.permissions import BasePermission

ADMIN_ROLES = ("admin", "superadmin")


class IsAdminOrSuperAdmin(BasePermission):
    """Allows access only to authenticated users with role admin/superadmin."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role in ADMIN_ROLES)
