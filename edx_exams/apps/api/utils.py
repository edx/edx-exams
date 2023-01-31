"""
API Utility Functions
"""
import logging
from datetime import timedelta

from django.utils import timezone

log = logging.getLogger(__name__)


def get_exam_attempt_time_remaining(exam_attempt, now=None):
    """
    For timed exam attempt, get the time remaining in seconds.

    If the end time has already passed, set time remaining to zero.
    """
    if exam_attempt.start_time is None or exam_attempt.allowed_time_limit_mins is None:
        return 0

    now = now or timezone.now()

    # Calculate end of attempt time
    end_time = exam_attempt.start_time + timedelta(minutes=exam_attempt.allowed_time_limit_mins)

    # Compare end of attempt time to now
    # If end time has passed, set to zero
    if end_time > now:
        secs_to_end = 0
    # Else calculate seconds remaining for attempt
    else:
        secs_to_end = (now - end_time).total_seconds()

    return secs_to_end
