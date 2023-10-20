"""
Handles sending emails to users about proctoring status changes.
"""
import logging

from django.conf import settings
from django.core.mail.message import EmailMessage
from django.template import loader

from edx_exams.apps.core.exam_types import get_exam_type
from edx_exams.apps.core.statuses import ExamAttemptStatus

log = logging.getLogger(__name__)


def send_attempt_status_email(attempt):
    """
    Send email for attempt status if necessary
    """
    exam = attempt.exam
    exam_type = get_exam_type(exam.exam_type)

    # do not send emails on practice exams or non-proctored exams
    if not exam_type.is_proctored or exam_type.is_practice:
        return

    if attempt.status == ExamAttemptStatus.submitted:
        email_template = 'email/proctoring_attempt_submitted.html'
    elif attempt.status == ExamAttemptStatus.verified:
        email_template = 'email/proctoring_attempt_verified.html'
    elif attempt.status == ExamAttemptStatus.rejected:
        email_template = 'email/proctoring_attempt_rejected.html'
    else:
        return  # do not send emails for other statuses

    email_template = loader.get_template(email_template)
    course_url = f'{settings.LEARNING_MICROFRONTEND_URL}/course/{exam.course_id}'
    contact_url = exam.provider.tech_support_email

    email_subject = f'Proctored exam {exam.exam_name} for user {attempt.user.username}'
    body = email_template.render({
        'exam_name': exam.exam_name,
        'course_url': course_url,
        'contact_url': contact_url,
    })

    email = EmailMessage(
        subject=email_subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[attempt.user.email],
    )
    email.content_subtype = 'html'

    try:
        email.send()
    except Exception as err: # pylint: disable=broad-except
        log.error(
            'Error while sending proctoring status email for '
            f'user_id {attempt.user.id}, exam_id {exam.id}: {err}'
        )
