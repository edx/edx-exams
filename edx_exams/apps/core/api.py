"""
Library for the edx-exams service.
"""
import logging
from datetime import datetime, timedelta

import pytz
from django.conf import settings
from django.utils import dateparse, timezone
from opaque_keys.edx.keys import CourseKey, UsageKey

from edx_exams.apps.core.data import CourseExamConfigurationData
from edx_exams.apps.core.email import send_attempt_status_email
from edx_exams.apps.core.exam_types import OnboardingExamType, PracticeExamType, get_exam_type
from edx_exams.apps.core.exceptions import (
    ExamAttemptAlreadyExists,
    ExamAttemptOnPastDueExam,
    ExamDoesNotExist,
    ExamIllegalStatusTransition
)
from edx_exams.apps.core.models import CourseExamConfiguration, Exam, ExamAttempt, ProctoringProvider
from edx_exams.apps.core.signals.signals import (
    emit_exam_attempt_errored_event,
    emit_exam_attempt_rejected_event,
    emit_exam_attempt_reset_event,
    emit_exam_attempt_submitted_event,
    emit_exam_attempt_verified_event
)
from edx_exams.apps.core.statuses import ExamAttemptStatus

log = logging.getLogger(__name__)


def get_exam_attempts(exam_id):
    """
    Return all attempts for an exam
    """
    return ExamAttempt.objects.filter(exam_id=exam_id).order_by('-created')


def get_attempt_by_id(attempt_id):
    """
    Return an attempt by id
    """
    attempt = ExamAttempt.get_attempt_by_id(attempt_id)

    return attempt


def get_active_attempt_for_user(user_id):
    """
    Find the currently running attempt for a user if it exists.
    """
    return ExamAttempt.get_active_attempt_for_user(user_id)


def get_attempt_for_user_with_attempt_number_and_resource_id(user_id, attempt_number, resource_id):
    """
    Retrieve an attempt in an exam described by resource_id for a user described by user_id with a particular attempt
    number described by attempt_number.
    """
    return ExamAttempt.get_attempt_for_user_with_attempt_number_and_resource_id(
        user_id,
        attempt_number,
        resource_id,
    )


def update_attempt_status(attempt_id, to_status):
    """
    Function to handle state transition of attempt status. Checks that status transition
    is allowed before updating attempt.
    """

    attempt_obj = ExamAttempt.get_attempt_by_id(attempt_id)

    exam_id = attempt_obj.exam.id
    user_id = attempt_obj.user.id

    from_status = attempt_obj.status

    log.info(
        'Updating attempt status for exam_id=%(exam_id)s for user_id=%(user_id)s '
        'from status "%(from_status)s" to "%(to_status)s"',
        {
            'exam_id': exam_id,
            'user_id': user_id,
            'from_status': from_status,
            'to_status': to_status,
        }
    )

    is_allowed_transition, error_msg = _allow_status_transition(attempt_obj, to_status)
    if not is_allowed_transition:
        raise ExamIllegalStatusTransition(error_msg)

    if to_status == ExamAttemptStatus.started:
        allowed_to_start, error_msg = _check_exam_is_allowed_to_start(attempt_obj, user_id)
        if not allowed_to_start:
            raise ExamIllegalStatusTransition(error_msg)

        attempt_obj.start_time = datetime.now(pytz.UTC)
        attempt_obj.allowed_time_limit_mins = _calculate_allowed_mins(attempt_obj.exam)

    course_key = CourseKey.from_string(attempt_obj.exam.course_id)
    usage_key = UsageKey.from_string(attempt_obj.exam.content_id)

    if to_status == ExamAttemptStatus.submitted:
        attempt_obj.end_time = datetime.now(pytz.UTC)

        emit_exam_attempt_submitted_event(
            attempt_obj.user,
            course_key,
            usage_key,
            attempt_obj.exam.exam_type
        )

    if to_status == ExamAttemptStatus.verified:
        emit_exam_attempt_verified_event(
            attempt_obj.user,
            course_key,
            usage_key,
            attempt_obj.exam.exam_type
        )

    if to_status == ExamAttemptStatus.rejected:
        emit_exam_attempt_rejected_event(
            attempt_obj.user,
            course_key,
            usage_key,
            attempt_obj.exam.exam_type
        )

    if to_status == ExamAttemptStatus.error:
        emit_exam_attempt_errored_event(
            attempt_obj.user,
            course_key,
            usage_key,
            attempt_obj.exam.exam_type
        )

    attempt_obj.status = to_status
    attempt_obj.save()

    escalation_email = get_escalation_email(exam_id)
    send_attempt_status_email(attempt_obj, escalation_email)

    return attempt_id


def reset_exam_attempt(attempt, requesting_user):
    """
    Reset an exam attempt
    """
    course_key = CourseKey.from_string(attempt.exam.course_id)
    usage_key = UsageKey.from_string(attempt.exam.content_id)

    log.info(
        f'Resetting exam attempt for user_id={attempt.user.id} in exam={attempt.exam.id} '
    )

    attempt.delete()
    emit_exam_attempt_reset_event(
        attempt.user,
        course_key,
        usage_key,
        attempt.exam.exam_type,
        requesting_user
    )


def _allow_status_transition(attempt_obj, to_status):
    """
    Helper method to assert that a given status transition is allowed
    """
    # check that status is legal
    is_transition_legal = ExamAttemptStatus.is_status_transition_legal(attempt_obj.status, to_status)
    if not is_transition_legal:
        illegal_status_transition_msg = (
            f'A status transition from "{attempt_obj.status}" to "{to_status}" was attempted '
            f'on exam_id={attempt_obj.exam.id} for user_id={attempt_obj.user.id}. This is not '
            f'allowed! (course_id={attempt_obj.exam.course_id})'
        )
        return False, illegal_status_transition_msg
    return True, ''


def _check_exam_is_allowed_to_start(attempt_obj, user_id):
    """
    Helper method to assert if an exam is allowed to start
    """
    # Check the attempt not already "started" and no start time exists
    exam_already_started = attempt_obj.status == ExamAttemptStatus.started and attempt_obj.start_time
    if exam_already_started:
        illegal_start_msg = (
            f'Cannot start exam attempt for exam_id={attempt_obj.exam.id} '
            f'and user_id={attempt_obj.user.id} because it has already started!'
        )
        return False, illegal_start_msg

    # Check that there are no other active exam attempts for the user
    no_other_active_attempts = ExamAttempt.check_no_other_active_attempts_for_user(user_id, attempt_obj.id)
    if not no_other_active_attempts:
        only_one_active_attempt_msg = (
            f'Cannot start exam attempt for exam_id={attempt_obj.exam.id} '
            f'and user_id={attempt_obj.user.id} because another exam attempt '
            f'is currently active!'
        )
        return False, only_one_active_attempt_msg
    return True, ''


def _calculate_allowed_mins(exam):
    """
    Calculate the allowed minutes for an attempt, taking due date into account
    If an exam's duration + start time exceeds the due date, return the remaining time between
    due date and the current time
    """
    due_datetime = exam.due_date
    allowed_time_limit_mins = exam.time_limit_mins

    if due_datetime:
        current_datetime = datetime.now(pytz.UTC)
        if current_datetime + timedelta(minutes=allowed_time_limit_mins) > due_datetime:
            # necessary to choose the maximum to prevent negative exam durations
            allowed_time_limit_mins = max(int((due_datetime - current_datetime).total_seconds() / 60), 0)

    return allowed_time_limit_mins


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
    if now > end_time:
        secs_to_end = 0
    # Else calculate seconds remaining for attempt
    else:
        secs_to_end = (end_time-now).total_seconds()

    return secs_to_end


def check_if_exam_timed_out(exam_attempt):
    """
    If an exam attempt's time remaining = 0 AND is in-progress/not submitted,
    change the status of an exam attempt to 'submitted', then return attempt_id.
    Return None otherwise.
    """

    exam_in_progress = exam_attempt.status in ExamAttemptStatus.in_progress_statuses
    exam_timed_out = get_exam_attempt_time_remaining(exam_attempt) == 0
    if exam_in_progress and exam_timed_out:
        log.info(
            ('Exam attempt with attempt_id=%(attempt_id)s for exam_id=%(exam_id)s for user_id=%(user_id)s '
             'in course_id=%(course_id)s has timed out.'),
            {
                'attempt_id': exam_attempt.id,
                'exam_id': exam_attempt.exam.id,
                'user_id': exam_attempt.user.id,
                'course_id': exam_attempt.exam.course_id
            }
        )

        updated_attempt_id = update_attempt_status(exam_attempt.id, ExamAttemptStatus.submitted)

        # Return latest attempt data if it was updated
        return get_attempt_by_id(updated_attempt_id)

    return exam_attempt


def create_exam_attempt(exam_id, user_id):
    """
    Creates an exam attempt for user_id against exam_id. There should only
    be one exam_attempt per user per exam.
    """

    exam_obj = Exam.get_exam_by_id(exam_id)

    if exam_obj is None:
        err_msg = (
            f'Exam with exam_id={exam_id} does not exist.'
        )
        raise ExamDoesNotExist(err_msg)

    if ExamAttempt.get_current_exam_attempt(user_id, exam_id) is not None:
        err_msg = (
            f'Cannot create attempt for exam_id={exam_id} and user_id={user_id} '
            f'because an attempt already exists.'
        )
        raise ExamAttemptAlreadyExists(err_msg)

    log.info(
        ('Creating exam attempt for exam_id=%(exam_id)s for user_id=%(user_id)s '
         'in course_id=%(course_id)s'),
        {
            'exam_id': exam_id,
            'user_id': user_id,
            'course_id': exam_obj.course_id,
        }
    )

    practice_exam_types = [PracticeExamType, OnboardingExamType]

    # if exam is past the due date, and it is a non-practice exam, raise error
    if (
        get_exam_type(exam_obj.exam_type) not in practice_exam_types
        and exam_obj.due_date
        and timezone.now() > exam_obj.due_date
    ):
        err_msg = (
            f'user_id={user_id} trying to create exam attempt for past due non-practice exam '
            f'exam_id={exam_id} in course_id={exam_obj.course_id}. Do not register an exam attempt!'
        )
        raise ExamAttemptOnPastDueExam(err_msg)

    # because we only support one attempt per exam per user,
    # always set the attempt number to 1 when creating an attempt
    attempt_number = 1

    # create exam attempt
    attempt = ExamAttempt.objects.create(
        exam_id=exam_id,
        user_id=user_id,
        status=ExamAttemptStatus.created,
        attempt_number=attempt_number,
    )

    log.info(
        ('Created exam attempt_id=%(attempt_id)s for exam_id=%(exam_id)s for '
         'user_id=%(user_id)s.'),
        {
            'attempt_id': attempt.id,
            'exam_id': exam_id,
            'user_id': user_id,
        }
    )

    return attempt.id


def get_exam_by_content_id(content_id):
    """
    Retrieve an exam filtered by content_id
    """
    try:
        exam = Exam.objects.get(content_id=content_id, is_active=True)
        return exam
    except Exam.DoesNotExist:
        return None


def get_exam_by_id(exam_id):
    """
    Retrieve an exam by id
    """
    try:
        exam = Exam.objects.get(id=exam_id)
        return exam
    except Exam.DoesNotExist:
        return None


def get_course_exams(course_id):
    """
    Retrieve all active exams for a course
    """
    return Exam.objects.filter(course_id=course_id, is_active=True)


def get_current_exam_attempt(user_id, exam_id):
    """
    Retrieve the current attempt for a user given an exam
    """
    attempt = ExamAttempt.get_current_exam_attempt(user_id, exam_id)
    return attempt


def get_exam_url_path(course_id, content_id):
    """
    Return a path to an exam in the Learning MFE given a course and content id
    """
    course_key = CourseKey.from_string(course_id)
    usage_key = UsageKey.from_string(content_id)
    url = f'{settings.LEARNING_MICROFRONTEND_URL}/course/{course_key}/{usage_key}'
    return url


def get_provider_by_exam_id(exam_id):
    """
    Return an exam configuration object
    """
    try:
        exam = Exam.objects.select_related('provider').get(id=exam_id)
        return exam.provider
    except Exam.DoesNotExist:
        return None


def is_exam_passed_due(exam):
    """
    Return whether the exam is passed due.

    Parameters:
        * exam: a serialized representation of the exam
    """
    due_date = exam['due_date']

    # In certain cases, an exam may not have a due date. In this case, the exam is never passed due.
    if due_date:
        due_date = dateparse.parse_datetime(due_date)
        return due_date <= datetime.now(pytz.UTC)
    return False


def get_escalation_email(exam_id):
    """
    Return contact details for the course exam configuration. These details describe who learners should reach out to
    for support with proctored exams.

    Parameters:
        * exam_id: the ID representing the exam

    Returns:
        * escalation_email: the escalation_email registered to the course in which the exam is configured, if there is
                            one; else, None.
    """
    exam_obj = Exam.get_exam_by_id(exam_id)

    try:
        course_config = CourseExamConfiguration.objects.get(course_id=exam_obj.course_id)
    except CourseExamConfiguration.DoesNotExist:
        return None
    else:
        return course_config.escalation_email


def create_or_update_course_exam_configuration(course_id, provider_name, escalation_email):
    """
    Create or update the exam configuration for a course specified by course_id. If the course exam configuration
    does not yet exist, create one with the provider set to the provider associated with the provider_name and the
    escalation_email set to the escalation_email.

    Parameters:
        * course_id: the ID representing the course
        * provider_name: the name of the proctoring provider
        * escalation_email: the escalation email
    """
    if provider_name is not None:
        provider = ProctoringProvider.objects.get(name=provider_name)
    else:
        # If the provider is set to None, then we must clear the escalation_email,
        # even if a non-null value is provided.
        escalation_email = None
        provider = None

    CourseExamConfiguration.create_or_update(course_id, provider, escalation_email)


def get_course_exam_configuration_by_course_id(course_id):
    """
    Return an instance of the CourseExamConfigurationData class representing the course exam configuration associated
    with the course ID.

    Parameters:
        * course_id: the ID representing the course

    Returns:
        * an instance of the CourseExamConfigurationData class, if the associated CourseExamConfiguration object exists;
          else, None.
    """
    # TODO: When the legacy service is deprecated, we should add a try...except block here. Currently, there isn't
    #       one because the router middleware will forward a request to the legacy service if there is no
    #       CourseExamConfiguration associated for a course before this code ever runs. Adding a try...except block
    #       here is just dead code.
    config = CourseExamConfiguration.objects.select_related('provider').get(course_id=course_id)
    return CourseExamConfigurationData(
        course_id=config.course_id,
        provider=config.provider.name,
        allow_opt_out=config.allow_opt_out,
        escalation_email=config.escalation_email,
    )
