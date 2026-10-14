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


class ServiceUserPermissions(BasePermission):
    """
    Permission class that only admits service accounts (the LMS worker) and global staff.

    Course staff are deliberately excluded: the endpoints using this permission expose
    data about arbitrary learners and are meant for backend-to-backend calls only.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


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
