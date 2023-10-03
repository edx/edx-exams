"""
Test signal handlers.
"""
import itertools
import uuid
from unittest.mock import patch

from ddt import ddt, idata, unpack
from django.test import TestCase

from edx_exams.apps.core.models import Exam, ExamAttempt, ProctoringProvider
from edx_exams.apps.core.statuses import ExamAttemptStatus
from edx_exams.apps.core.test_utils.factories import UserFactory
from edx_exams.apps.lti.signals.handlers import assessment_started


@ddt
class TestAssessmentStarted(TestCase):
    """
    Test the assessment_started signal handler.
    """

    def setUp(self):
        super().setUp()

        self.user = UserFactory(username='test', is_active=True, is_staff=False)
        self.user.set_password('password')
        self.user.save()

        self.test_provider = ProctoringProvider.objects.create(
            name='test_provider',
            verbose_name='testing provider',
            lti_configuration_id='123456789',
            tech_support_phone='1118976309',
            tech_support_email='test@example.com',
        )

        self.course_id = 'course-v1:edx+test+f19'
        self.content_id = 'block-v1:edX+test+2023+type@sequential+block@1111111111'

        self.exam = Exam.objects.create(
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id=self.content_id,
            exam_name='test_exam',
            exam_type='proctored',
            time_limit_mins=30,
            due_date='2021-07-01 00:00:00',
            hide_after_due=False,
            is_active=True
        )

        self.attempt = ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1111111,
            status=ExamAttemptStatus.created,
            start_time=None,
            allowed_time_limit_mins=None,
        )

    def test_assessment_started_updated_attempt(self):
        """
        Test that the assessment_started signal handler updates the attempt described by the kwargs to the
        ready_to_start state.
        """
        kwargs = {
            'user_id': self.user.id,
            'attempt_number': self.attempt.attempt_number,
            'resource_link': {'id': self.exam.resource_id},
        }

        assessment_started(None, **kwargs)

        self.attempt.refresh_from_db()

        self.assertEqual(self.attempt.status, ExamAttemptStatus.ready_to_start)

    @patch('edx_exams.apps.lti.signals.handlers.update_attempt_status')
    @idata(itertools.product([1, None], [1, None], [None, uuid.uuid4()]))
    @unpack
    def test_assessment_started_invalid_kwargs(self, user_id, attempt_number, resource_id, mock_update_attempt_status):
        """
        Test that the assessment_started signal handler does not update call update_attempt_status when the
        LTI_1P3_PROCTORING_ASSESSMENT_STARTED kwargs are invalid (i.e. falsey).
        """
        kwargs = {
            'user_id': user_id,
            'attempt_number': attempt_number,
            'resource_link': {'id': resource_id},
        }

        assessment_started(None, **kwargs)

        assert not mock_update_attempt_status.called

    @patch('edx_exams.apps.lti.signals.handlers.update_attempt_status')
    def test_assessment_started_no_attempt(self, mock_update_attempt_status):
        """
        Test that the assessment_started signal handler does not update call update_attempt_status for the attempt
        described by the kwargs to the ready_to_start state when there is no attempt described by the kwargs.
        """
        kwargs = {
            'user_id': self.user.id,
            'attempt_number': 100,
            'resource_link': {'id': self.exam.resource_id},
        }

        assessment_started(None, **kwargs)

        assert not mock_update_attempt_status.called

    @patch('edx_exams.apps.lti.signals.handlers.update_attempt_status')
    def test_assessment_started_multiple_attempts(self, mock_update_attempt_status):
        """
        Test that the assessment_started signal handler does not update the attempts described by the kwargs to the
        ready_to_start state when there is more than one attempt described by the kwargs.
        """
        other_attempt = ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1111111,
            status=ExamAttemptStatus.created,
            start_time=None,
            allowed_time_limit_mins=None,
        )

        kwargs = {
            'user_id': self.user.id,
            'attempt_number': self.attempt.attempt_number,
            'resource_link': {'id': str(uuid.uuid4())},
        }

        assessment_started(None, **kwargs)

        self.attempt.refresh_from_db()

        # Both attempt's attempt status should remain unchanged because the kwargs refer to more than one attempt.
        assert not mock_update_attempt_status.called
        self.assertEqual(self.attempt.status, ExamAttemptStatus.created)
        self.assertEqual(other_attempt.status, ExamAttemptStatus.created)

    def test_assessment_started_illegal_transition(self):
        """
        Test that the assessment_started signal handler does not update the attempt described by the kwargs to the
        ready_to_start state when it would be an illegal status transition.
        """
        self.attempt.status = ExamAttemptStatus.submitted
        self.attempt.save()

        kwargs = {
            'user_id': self.user.id,
            'attempt_number': self.attempt.attempt_number,
            'resource_link': {'id': self.exam.resource_id},
        }

        assessment_started(None, **kwargs)

        self.attempt.refresh_from_db()

        # The attempt status should remain unchanged because the requested transition is illegal.
        self.assertEqual(self.attempt.status, ExamAttemptStatus.submitted)
