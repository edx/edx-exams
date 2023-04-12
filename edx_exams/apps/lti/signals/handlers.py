"""
edX Exams Signal Handlers
"""
import logging

from django.dispatch import receiver
from lti_consumer.signals.signals import LTI_1P3_PROCTORING_ASSESSMENT_STARTED

from edx_exams.apps.core.api import get_attempt_for_user_with_attempt_number_and_resource_id, update_attempt_status
from edx_exams.apps.core.exceptions import ExamIllegalStatusTransition
from edx_exams.apps.core.statuses import ExamAttemptStatus

log = logging.getLogger(__name__)


@receiver(LTI_1P3_PROCTORING_ASSESSMENT_STARTED)
def assessment_started(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Signal handler for the lti_consumer LTI_1P3_PROCTORING_ASSESSMENT_STARTED signal.
    """
    user_id = kwargs.get('user_id')
    attempt_number = kwargs.get('attempt_number')
    resource_id = kwargs.get('resource_id')

    if not user_id or not attempt_number or not resource_id:
        log.info(
            'expected valid values for LTI_1P3_PROCTORING_ASSESSMENT_STARTED signal kwargs but received '
            f'attempt_number={attempt_number}, user_id={user_id}, and resource_id={resource_id}.'
        )
        return

    attempt = get_attempt_for_user_with_attempt_number_and_resource_id(
        user_id,
        attempt_number,
        resource_id,
    )

    if not attempt:
        log.info(
            f'attempt_number={attempt_number} for user_id={user_id} in exam with resource_id={resource_id} is '
            'not associated with a single attempt.'
        )
        return

    try:
        update_attempt_status(attempt.id, ExamAttemptStatus.ready_to_start)
    except ExamIllegalStatusTransition:
        log.info(
            f'user_id={attempt.user.id} attempted to update attempt_id={attempt.id} in '
            f'course_id={attempt.exam.course_id} from status={attempt.status} to '
            f'status={ExamAttemptStatus.ready_to_start}, but this status '
            f'transition is illegal.'
        )
