"""
Signal handlers for the edx-exams application.
"""
from django.conf import settings
from django.dispatch import receiver
from openedx_events.event_bus import get_producer
from openedx_events.learning.signals import (
    EXAM_ATTEMPT_ERRORED,
    EXAM_ATTEMPT_REJECTED,
    EXAM_ATTEMPT_SUBMITTED,
    EXAM_ATTEMPT_VERIFIED
)

topic_name = getattr(settings, 'EXAM_ATTEMPT_EVENTS_KAFKA_TOPIC_NAME', '')


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
