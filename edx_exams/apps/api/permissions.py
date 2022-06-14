""" Permissions for edx-exams API"""
from rest_framework.permissions import BasePermission


class StaffUserPermissions(BasePermission):
    """ Permission class to check if user is staff """

    def has_permission(self, request, view):
        return request.user.is_staff
