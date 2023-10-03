"""
Signal handlers for the edx-exams application.
"""
from django.dispatch import receiver
from openedx_events.event_bus import get_producer
from openedx_events.learning.signals import (
    EXAM_ATTEMPT_ERRORED,
    EXAM_ATTEMPT_REJECTED,
    EXAM_ATTEMPT_SUBMITTED,
    EXAM_ATTEMPT_VERIFIED
)


@receiver(EXAM_ATTEMPT_SUBMITTED)
def listen_for_exam_attempt_submitted(sender, signal, **kwargs):  # pylint: disable=unused-argument
    """
    Publish EXAM_ATTEMPT_SUBMITTED signals onto the event bus.
    """
    get_producer().send(
        signal=EXAM_ATTEMPT_SUBMITTED,
        topic='exam-attempt-submitted',
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
        topic='exam-attempt-verified',
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
        topic='exam-attempt-rejected',
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
        topic='exam-attempt-errored',
        event_key_field='exam_attempt.course_key',
        event_data={'exam_attempt': kwargs['exam_attempt']},
        event_metadata=kwargs['metadata'],
    )
