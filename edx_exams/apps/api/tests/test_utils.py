"""
Tests for API utility functions
"""
import uuid
from datetime import datetime

from edx_exams.apps.api.test_utils import ExamsAPITestCase
from edx_exams.apps.api.utils import get_exam_attempt_time_remaining
from edx_exams.apps.core.models import Exam, ExamAttempt

test_start_time = datetime(2023, 11, 4, 11, 5, 23)
test_time_limit_mins = 30


class TestUtils(ExamsAPITestCase):
    """
    Tests for API Utility Functions.
    """
    def setUp(self):
        super().setUp()

        self.course_id = 'course-v1:edx+test+f19'
        self.exam = Exam.objects.create(
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id='abcd1234',
            exam_name='test_exam',
            exam_type='proctored',
            time_limit_mins=30,
        )

        self.exam_attempt = ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1,
            status='started',
            start_time=test_start_time,
            allowed_time_limit_mins=test_time_limit_mins
        )

    def test_get_exam_attempt_time_remaining_zero(self):
        """
        Verify that there is zero time remaining for exam attempt.
        """
        test_now = datetime(2023, 11, 4, 11, 35, 23)
        time_left = get_exam_attempt_time_remaining(self.exam_attempt, test_now)
        self.assertEqual(0, time_left)

    def test_get_exam_attempt_time_remaining_past_due(self):
        """
        Verify that exam attempt that is past due returns zero.
        """
        test_now = datetime(2023, 11, 4, 2, 5, 23)
        time_left = get_exam_attempt_time_remaining(self.exam_attempt, test_now)
        self.assertEqual(0, time_left)

    def test_get_exam_attempt_time_remaining_time_left(self):
        """
        Verify that exam attempt time remaining is correct.
        """
        test_now = datetime(2023, 11, 4, 12, 5, 23)
        time_left = get_exam_attempt_time_remaining(self.exam_attempt, test_now)
        self.assertEqual(1800, time_left)

    def test_get_exam_attempt_missing_start_time(self):
        """
        Verify 0 due to missing start time.
        """
        test_now = datetime(2023, 11, 4, 0, 5, 23)
        exam_attempt = ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1,
            status='started',
            allowed_time_limit_mins=test_time_limit_mins
        )

        time_left = get_exam_attempt_time_remaining(exam_attempt, test_now)
        self.assertEqual(0, time_left)

    def test_get_exam_attempt_missing_time_limit(self):
        """
        Verify 0 due to missing time limit.
        """
        test_now = datetime(2023, 11, 4, 0, 5, 23)
        exam_attempt = ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1,
            status='started',
            allowed_time_limit_mins=test_time_limit_mins
        )

        time_left = get_exam_attempt_time_remaining(exam_attempt, test_now)
        self.assertEqual(0, time_left)
