""" Permissions for edx-exams API"""
from rest_framework.permissions import BasePermission


class CourseStaffUserPermissions(BasePermission):
    """ Permission class to check if user has course staff permissions """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if view.kwargs.get('course_id'):
            return request.user.is_staff or request.user.has_course_staff_permission(view.kwargs['course_id'])
        # right now we don't have any views that use this
        return request.user.is_staff  # pragma: no cover


class CourseStaffOrReadOnlyPermissions(CourseStaffUserPermissions):
    """
    Permission class granting write access to course staff users
    and read-only access to other authenticated users
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.method == 'GET':
            return True
        else:
            return super().has_permission(request, view)
