""" Permissions for edx-exams API"""
from rest_framework.permissions import BasePermission


class StaffUserPermissions(BasePermission):
    """ Permission class to check if user is staff """

    def has_permission(self, request, view):
        return request.user.is_staff


class StaffUserOrReadOnlyPermissions(BasePermission):
    """
    Permission class granting write access to staff users and
    read-only access to authenticated users
    """
    def has_permission(self, request, view):
        return request.user.is_staff or (
            request.user.is_authenticated and
            request.method == 'GET'
        )
