"""
Signal definitions and functions to send those signals for the edx-exams application.
"""

from openedx_events.learning.data import ExamAttemptData, UserData, UserPersonalData
from openedx_events.learning.signals import EXAM_ATTEMPT_REJECTED, EXAM_ATTEMPT_SUBMITTED, EXAM_ATTEMPT_VERIFIED


def emit_exam_attempt_submitted_event(user, course_key, usage_key, exam_type):
    """
    Emit the EXAM_ATTEMPT_SUBMITTED Open edX event.
    """
    user_data = UserData(
        id=user.id,
        is_active=user.is_active,
        pii=UserPersonalData(
            username=user.username,
            email=user.email,
            name=user.full_name
        )
    )

    # .. event_implemented_name: EXAM_ATTEMPT_SUBMITTED
    EXAM_ATTEMPT_SUBMITTED.send_event(
        exam_attempt=ExamAttemptData(
            student_user=user_data,
            course_key=course_key,
            usage_key=usage_key,
            exam_type=exam_type,
            requesting_user=user_data
        )
    )


def emit_exam_attempt_verified_event(user, course_key, usage_key, exam_type):
    """
    Emit the EXAM_ATTEMPT_VERIFIED Open edX event.
    """
    user_data = UserData(
        id=user.id,
        is_active=user.is_active,
        pii=UserPersonalData(
            username=user.username,
            email=user.email,
            name=user.full_name
        )
    )

    # .. event_implemented_name: EXAM_ATTEMPT_VERIFIED
    EXAM_ATTEMPT_VERIFIED.send_event(
        exam_attempt=ExamAttemptData(
            student_user=user_data,
            course_key=course_key,
            usage_key=usage_key,
            exam_type=exam_type
        )
    )


def emit_exam_attempt_rejected_event(user, course_key, usage_key, exam_type):
    """
    Emit the EXAM_ATTEMPT_REJECTED Open edX event.
    """
    user_data = UserData(
        id=user.id,
        is_active=user.is_active,
        pii=UserPersonalData(
            username=user.username,
            email=user.email,
            name=user.full_name
        )
    )

    # .. event_implemented_name: EXAM_ATTEMPT_REJECTED
    EXAM_ATTEMPT_REJECTED.send_event(
        exam_attempt=ExamAttemptData(
            student_user=user_data,
            course_key=course_key,
            usage_key=usage_key,
            exam_type=exam_type
        )
    )
