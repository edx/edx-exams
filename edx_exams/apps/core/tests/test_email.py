"""
Test email notifications for attempt status change
"""

import ddt
import mock
from django.core import mail
from django.test import TestCase

from edx_exams.apps.core.api import update_attempt_status
from edx_exams.apps.core.test_utils.factories import ExamAttemptFactory, ExamFactory, UserFactory


@ddt.ddt
class TestEmail(TestCase):
    """
    Test email notifications for attempt status change
    """
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        self.proctored_exam = ExamFactory.create(
            exam_type='proctored',
        )
        self.started_attempt = ExamAttemptFactory.create(
            exam=self.proctored_exam,
            user=self.user,
            status='started',
        )

    @staticmethod
    def _normalize_whitespace(string):
        """
        Replaces newlines and multiple spaces with a single space.
        """
        return ' '.join(string.replace('\n', '').split())

    @ddt.data(
        ('submitted', 'was submitted successfully'),
        ('verified', 'was reviewed and you met all proctoring requirements'),
        ('rejected', 'the course team has identified one or more violations'),
    )
    @ddt.unpack
    def test_send_email(self, status, expected_message):
        """
        Test correct message is sent for statuses that trigger an email
        """
        update_attempt_status(self.started_attempt.id, status)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.started_attempt.user.email, mail.outbox[0].to)
        self.assertIn(expected_message, self._normalize_whitespace(mail.outbox[0].body))

    @mock.patch('edx_exams.apps.core.email.log.error')
    def test_send_email_failure(self, mock_log_error):
        """
        Test error is logged when an email fails to send
        """
        with mock.patch('edx_exams.apps.core.email.EmailMessage.send', side_effect=Exception):
            update_attempt_status(self.started_attempt.id, 'submitted')
        mock_log_error.assert_called_once()
        self.assertIn('Error while sending proctoring status email', mock_log_error.call_args[0][0])

    @ddt.data(
        'created',
        'ready_to_start',
        'download_software_clicked',
        'started',
        'ready_to_submit',
        'error',
    )
    def test_status_should_not_send_email(self, status):
        """
        Test no email is sent for statuses that should not trigger
        """
        update_attempt_status(self.started_attempt.id, status)
        self.assertEqual(len(mail.outbox), 0)

    def test_non_proctored_exam_should_not_send_email(self):
        """
        Test no email is sent for non-proctored exams
        """
        timed_attempt = ExamAttemptFactory.create(
            exam=ExamFactory.create(
                exam_type='timed',
            ),
            user=self.user,
            status='started',
        )
        update_attempt_status(timed_attempt.id, 'submitted')
        self.assertEqual(len(mail.outbox), 0)

    def test_practice_exam_should_not_send_email(self):
        """
        Test no email is sent for practice exams
        """
        practice_proctored_attempt = ExamAttemptFactory.create(
            exam=ExamFactory.create(
                exam_type='onboarding',
            ),
            user=self.user,
            status='started',
        )
        update_attempt_status(practice_proctored_attempt.id, 'submitted')
        self.assertEqual(len(mail.outbox), 0)
