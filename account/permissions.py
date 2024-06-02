from rest_framework import permissions


class IsSuperAdminOrIsAdminOrIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow read access to authenticated users
        if view.action in ['list', 'retrieve']:
            return request.user and request.user.is_authenticated

        # For 'admin' users, full CRUD access
        if request.user and request.user.groups.filter(name='Admin').exists():
            return True

        # For '' users, allow access for CRU
        if request.user and request.user.groups.filter(name='General User').exists():
            return view.action in ['list', 'retrieve', 'update']

        return False
