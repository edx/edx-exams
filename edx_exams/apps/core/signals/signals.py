"""
Signal definitions and functions to send those signals for the edx-exams application.
"""

from openedx_events.learning.data import ExamAttemptData, UserData, UserPersonalData
from openedx_events.learning.signals import (
    EXAM_ATTEMPT_ERRORED,
    EXAM_ATTEMPT_REJECTED,
    EXAM_ATTEMPT_RESET,
    EXAM_ATTEMPT_SUBMITTED,
    EXAM_ATTEMPT_VERIFIED
)


def _create_user_data(user):
    """
    Helper function to create a UserData object.
    """
    user_data = UserData(
        id=1, #TODO: put this back: user.lms_user_id,
        is_active=user.is_active,
        pii=UserPersonalData(
            username=user.username,
            email=user.email,
            name=user.full_name
        )
    )

    return user_data


def emit_exam_attempt_submitted_event(user, course_key, usage_key, exam_type):
    """
    Emit the EXAM_ATTEMPT_SUBMITTED Open edX event.
    """
    user_data = _create_user_data(user)

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
    user_data = _create_user_data(user)

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
    user_data = _create_user_data(user)

    # .. event_implemented_name: EXAM_ATTEMPT_REJECTED
    EXAM_ATTEMPT_REJECTED.send_event(
        exam_attempt=ExamAttemptData(
            student_user=user_data,
            course_key=course_key,
            usage_key=usage_key,
            exam_type=exam_type
        )
    )


def emit_exam_attempt_errored_event(user, course_key, usage_key, exam_type):
    """
    Emit the EXAM_ATTEMPT_ERRORED Open edX event.
    """
    user_data = _create_user_data(user)

    # .. event_implemented_name: EXAM_ATTEMPT_ERRORED
    EXAM_ATTEMPT_ERRORED.send_event(
        exam_attempt=ExamAttemptData(
            student_user=user_data,
            course_key=course_key,
            usage_key=usage_key,
            exam_type=exam_type
        )
    )


def emit_exam_attempt_reset_event(user, course_key, usage_key, exam_type, requesting_user):
    """
    Emit the EXAM_ATTEMPT_RESET Open edX event.
    """
    user_data = _create_user_data(user)
    requesting_user_data = _create_user_data(requesting_user)

    # .. event_implemented_name: EXAM_ATTEMPT_RESET
    EXAM_ATTEMPT_RESET.send_event(
        exam_attempt=ExamAttemptData(
            student_user=user_data,
            course_key=course_key,
            usage_key=usage_key,
            exam_type=exam_type,
            requesting_user=requesting_user_data
        )
    )
