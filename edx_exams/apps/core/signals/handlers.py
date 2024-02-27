"""
Signal handlers for the edx-exams application.
"""
from django.conf import settings
from django.dispatch import receiver
from openedx_events.event_bus import get_producer
from openedx_events.learning.signals import (
    COURSE_ACCESS_ROLE_ADDED,
    COURSE_ACCESS_ROLE_REMOVED,
    EXAM_ATTEMPT_ERRORED,
    EXAM_ATTEMPT_REJECTED,
    EXAM_ATTEMPT_RESET,
    EXAM_ATTEMPT_SUBMITTED,
    EXAM_ATTEMPT_VERIFIED
)

from edx_exams.apps.core.models import CourseStaffRole, User

topic_name = getattr(settings, 'EXAM_ATTEMPT_EVENTS_KAFKA_TOPIC_NAME', '')

# list of roles that grant access to instructor features for exams
COURSE_STAFF_ROLES = ['staff', 'instructor', 'limited_staff']


@receiver(EXAM_ATTEMPT_SUBMITTED)
def listen_for_exam_attempt_submitted(sender, signal, **kwargs):  # pylint: disable=unused-argument
    """
    Publish EXAM_ATTEMPT_SUBMITTED signals onto the event bus.
    """
    get_producer().send(
        signal=EXAM_ATTEMPT_SUBMITTED,
        topic=topic_name,
        event_key_field='exam_attempt.course_key',
        event_data={'exam_attempt': kwargs['exam_attempt']},
        event_metadata=kwargs['metadata'],
    )


@receiver(EXAM_ATTEMPT_VERIFIED)
def listen_for_exam_attempt_verified(sender, signal, **kwargs):  # pylint: disable=unused-argument
    """
    Publish EXAM_ATTEMPT_VERIFIED signal onto the event bus
    """
    get_producer().send(
        signal=EXAM_ATTEMPT_VERIFIED,
        topic=topic_name,
        event_key_field='exam_attempt.course_key',
        event_data={'exam_attempt': kwargs['exam_attempt']},
        event_metadata=kwargs['metadata'],
    )


@receiver(EXAM_ATTEMPT_REJECTED)
def listen_for_exam_attempt_rejected(sender, signal, **kwargs):  # pylint: disable=unused-argument
    """
    Publish EXAM_ATTEMPT_REJECTED signal onto the event bus
    """
    get_producer().send(
        signal=EXAM_ATTEMPT_REJECTED,
        topic=topic_name,
        event_key_field='exam_attempt.course_key',
        event_data={'exam_attempt': kwargs['exam_attempt']},
        event_metadata=kwargs['metadata'],
    )


@receiver(EXAM_ATTEMPT_ERRORED)
def listen_for_exam_attempt_errored(sender, signal, **kwargs):  # pylint: disable=unused-argument
    """
    Publish EXAM_ATTEMPT_ERRORED signal onto the event bus
    """
    get_producer().send(
        signal=EXAM_ATTEMPT_ERRORED,
        topic=topic_name,
        event_key_field='exam_attempt.course_key',
        event_data={'exam_attempt': kwargs['exam_attempt']},
        event_metadata=kwargs['metadata'],
    )


@receiver(EXAM_ATTEMPT_RESET)
def listen_for_exam_attempt_reset(sender, signal, **kwargs):  # pylint: disable=unused-argument
    """
    Publish EXAM_ATTEMPT_RESET signal onto the event bus
    """
    get_producer().send(
        signal=EXAM_ATTEMPT_RESET,
        topic=topic_name,
        event_key_field='exam_attempt.course_key',
        event_data={'exam_attempt': kwargs['exam_attempt']},
        event_metadata=kwargs['metadata'],
    )


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

    user, created = User.objects.get_or_create(  # pylint: disable=unused-variable
        username=user_data.pii.username,
        email=user_data.pii.email,
    )
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
