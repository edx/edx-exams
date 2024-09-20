"""
Signal handlers for the edx-exams application.
"""
from django.dispatch import receiver
from openedx_events.learning.signals import COURSE_ACCESS_ROLE_ADDED, COURSE_ACCESS_ROLE_REMOVED

from edx_exams.apps.core.models import CourseStaffRole, User

# list of roles that grant access to instructor features for exams
COURSE_STAFF_ROLES = ['staff', 'instructor', 'limited_staff']


@receiver(COURSE_ACCESS_ROLE_ADDED)
def listen_for_course_access_role_added(sender, signal, **kwargs):  # pylint: disable=unused-argument
    """
    Recieve COURSE_ACCESS_ROLE_ADDED signal from the event bus
    """
    event_data = kwargs['course_access_role_data']
    user_data = event_data.user
    course_key = event_data.course_key
    role = event_data.role

    if role not in COURSE_STAFF_ROLES:
        return

    user, _ = User.objects.get_or_create(username=user_data.pii.username)
    CourseStaffRole.objects.get_or_create(
        user=user,
        course_id=course_key,
        role=role,
    )


@receiver(COURSE_ACCESS_ROLE_REMOVED)
def listen_for_course_access_role_removed(sender, signal, **kwargs):  # pylint: disable=unused-argument
    """
    Recieve COURSE_ACCESS_ROLE_REMOVED signal from the event bus
    """
    event_data = kwargs['course_access_role_data']
    user_data = event_data.user
    course_key = event_data.course_key
    role = event_data.role

    if role not in COURSE_STAFF_ROLES:
        return

    CourseStaffRole.objects.filter(
        user__username=user_data.pii.username,
        course_id=course_key,
        role=role,
    ).delete()
