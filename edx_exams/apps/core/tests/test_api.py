"""
Tests for API utility functions
"""
import uuid
from datetime import datetime, timedelta
from itertools import product

import ddt
from django.utils import timezone
from freezegun import freeze_time

from edx_exams.apps.api.serializers import ExamAttemptSerializer
from edx_exams.apps.api.test_utils import ExamsAPITestCase
from edx_exams.apps.core.api import (
    create_exam_attempt,
    get_attempt_by_id,
    get_exam_attempt_time_remaining,
    update_attempt_status
)
from edx_exams.apps.core.exceptions import (
    ExamAttemptAlreadyExists,
    ExamAttemptOnPastDueExam,
    ExamDoesNotExist,
    ExamIllegalStatusTransition
)
from edx_exams.apps.core.models import Exam, ExamAttempt
from edx_exams.apps.core.statuses import ExamAttemptStatus

test_start_time = datetime(2023, 11, 4, 11, 5, 23)
test_time_limit_mins = 30


class TestExamAttemptTimeRemaining(ExamsAPITestCase):
    """
    Tests for the API utility function `get_exam_attempt_time_remaining`
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
        test_now = datetime(2023, 11, 4, 13, 5, 23)
        time_left = get_exam_attempt_time_remaining(self.exam_attempt, test_now)
        self.assertEqual(0, time_left)

    def test_get_exam_attempt_time_remaining_time_left(self):
        """
        Verify that exam attempt time remaining is correct.
        """
        test_now = datetime(2023, 11, 4, 10, 5, 23)
        time_left = get_exam_attempt_time_remaining(self.exam_attempt, test_now)
        self.assertEqual(5400, time_left)

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


@ddt.ddt
class TestUpdateAttemptStatus(ExamsAPITestCase):
    """
    Tests for the API utility function `update_attempt_status`
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
            status=ExamAttemptStatus.created,
        )

    @ddt.data(
        ExamAttemptStatus.started,
        ExamAttemptStatus.ready_to_submit,
        ExamAttemptStatus.submitted,
        ExamAttemptStatus.download_software_clicked,
        ExamAttemptStatus.error,
    )
    def test_update_attempt(self, to_status):
        """
        Test that an attempt can be updated as expected
        """
        attempt_id = update_attempt_status(self.exam_attempt.id, to_status)
        updated_attempt = ExamAttempt.get_attempt_by_id(attempt_id)
        self.assertEqual(updated_attempt.status, to_status)

    def test_start_attempt(self):
        """
        Test that an exam can start
        """
        with freeze_time(timezone.now()):
            attempt_id = update_attempt_status(self.exam_attempt.id, ExamAttemptStatus.started)
            updated_attempt = ExamAttempt.get_attempt_by_id(attempt_id)
            self.assertEqual(updated_attempt.status, ExamAttemptStatus.started)
            self.assertEqual(updated_attempt.start_time, timezone.now())
            self.assertEqual(updated_attempt.allowed_time_limit_mins, self.exam.time_limit_mins)

    @ddt.data(
        True,
        False
    )
    def test_start_attempt_with_due_date(self, is_due_during_exam):
        """
        Test that an exam with a due date approaching returns the appropriate amount of time
        """
        time_to_due_date = 10 if is_due_during_exam else 60

        with freeze_time(timezone.now()):
            # create exam with due date in 10 minutes
            exam_with_due_date = Exam.objects.create(
                resource_id=str(uuid.uuid4()),
                course_id=self.course_id,
                provider=self.test_provider,
                content_id='abcd1234',
                exam_name='test_exam',
                exam_type='proctored',
                time_limit_mins=30,
                due_date=timezone.now() + timedelta(minutes=time_to_due_date)
            )
            attempt = ExamAttempt.objects.create(
                user=self.user,
                exam=exam_with_due_date,
                attempt_number=1,
                status=ExamAttemptStatus.created,
            )

            expected_allowed_time = 10 if is_due_during_exam else exam_with_due_date.time_limit_mins

            attempt_id = update_attempt_status(attempt.id, ExamAttemptStatus.started)
            updated_attempt = ExamAttempt.get_attempt_by_id(attempt_id)
            self.assertEqual(updated_attempt.status, ExamAttemptStatus.started)
            self.assertEqual(updated_attempt.start_time, timezone.now())
            self.assertEqual(updated_attempt.allowed_time_limit_mins, expected_allowed_time)

    def test_submit_attempt(self):
        """
        Test that an exam can be submitted
        """
        with freeze_time(timezone.now()):
            attempt_id = update_attempt_status(self.exam_attempt.id, ExamAttemptStatus.submitted)
            updated_attempt = ExamAttempt.get_attempt_by_id(attempt_id)
            self.assertEqual(updated_attempt.status, ExamAttemptStatus.submitted)
            self.assertEqual(updated_attempt.end_time, timezone.now())

    def test_illegal_start(self):
        """
        Test that an already started exam cannot be started
        """
        update_attempt_status(self.exam_attempt.id, ExamAttemptStatus.started)

        with self.assertRaises(ExamIllegalStatusTransition) as exc:
            # update again to started
            update_attempt_status(self.exam_attempt.id, ExamAttemptStatus.started)
        self.assertIn('Cannot start exam attempt', str(exc.exception))

    @ddt.data(
        *product(ExamAttemptStatus.completed_statuses, ExamAttemptStatus.incomplete_statuses)
    )
    @ddt.unpack
    def test_illegal_transition(self, from_status, to_status):
        """
        Test that an illegal transition raises exception
        """
        attempt = ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1,
            status=from_status,
        )

        with self.assertRaises(ExamIllegalStatusTransition) as exc:
            update_attempt_status(attempt.id, to_status)
        self.assertIn('A status transition from', str(exc.exception))


class TestGetAttemptById(ExamsAPITestCase):
    """
    Tests for the API utility function `get_attempt_by_id`
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
            status=ExamAttemptStatus.created,
        )

    def test_get_serialized_attempt(self):
        """
        Test that a serialized attempt is returned
        """
        attempt = get_attempt_by_id(self.exam_attempt.id)
        self.assertEqual(attempt, ExamAttemptSerializer(self.exam_attempt).data)

    def test_with_no_attempt(self):
        """
        Test that if the attempt does not exist, None is returned
        """
        self.assertIsNone(get_attempt_by_id(111111111))


@ddt.ddt
class TestCreateExamAttempt(ExamsAPITestCase):
    """
    Tests for the API utility function `create_exam_attempt`
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

    @ddt.data(
        'proctored',
        'timed',
    )
    def test_exam_passed_due(self, exam_type):
        """
        Test that we can not create an attempt for an exam that is passed due
        """

        # create exam that was due an hour ago
        passed_due_exam = Exam.objects.create(
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id='abcd1234',
            exam_name='test_exam',
            exam_type=exam_type,
            time_limit_mins=30,
            due_date=timezone.now() - timedelta(minutes=60)
        )

        with self.assertRaises(ExamAttemptOnPastDueExam) as exc:
            create_exam_attempt(passed_due_exam.id, self.user.id)

        self.assertIn('trying to create exam attempt for past due non-practice exam', str(exc.exception))

    @ddt.data(
        ('proctored', timedelta(minutes=60)),  # proctored exam, due in the future
        ('timed', timedelta(minutes=60)),  # timed exam, due in the future
        ('onboarding', timedelta(minutes=60)),  # onboarding exam, due in the future
        ('practice', timedelta(minutes=60)),  # practice exam, due in the future
        ('onboarding', -timedelta(minutes=60)),  # onboarding exam, passed due
        ('practice', -timedelta(minutes=60)),  # practice exam, passed due
    )
    @ddt.unpack
    def test_create_exam_attempt(self, exam_type, due_date_delta):
        """
        Test that we can create an exam attempt
        """
        exam = Exam.objects.create(
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id='abcd1234',
            exam_name='test_exam',
            exam_type=exam_type,
            time_limit_mins=30,
            due_date=timezone.now() + due_date_delta
        )

        attempt_id = create_exam_attempt(exam.id, self.user.id)
        attempt_obj = ExamAttempt.get_attempt_by_id(attempt_id)

        self.assertEqual(attempt_obj.status, ExamAttemptStatus.created)
        self.assertEqual(attempt_obj.exam_id, exam.id)
        self.assertEqual(attempt_obj.user_id, self.user.id)
        self.assertEqual(attempt_obj.attempt_number, 1)

    def test_bad_exam_id(self):
        """
        Test that a non existant exam raises an error
        """
        fake_exam_id = 11111111

        with self.assertRaises(ExamDoesNotExist) as exc:
            create_exam_attempt(fake_exam_id, self.user.id)

        err_msg = f'Exam with exam_id={fake_exam_id} does not exist.'
        self.assertEqual(err_msg, str(exc.exception))

    def test_attempt_already_exists(self):
        """
        Test that trying to create an attempt for a user that already has an attempt fails
        """
        ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1,
            status=ExamAttemptStatus.created,
        )

        exam_id = self.exam.id
        user_id = self.user.id

        with self.assertRaises(ExamAttemptAlreadyExists) as exc:
            create_exam_attempt(exam_id, user_id)

        err_msg = (
            f'Cannot create attempt for exam_id={exam_id} and user_id={user_id} '
            f'because an attempt already exists.'
        )
        self.assertEqual(err_msg, str(exc.exception))

        # check to ensure that only one attempt exists for exam and user
        filtered_attempts = ExamAttempt.objects.filter(user_id=user_id, exam_id=exam_id)
        self.assertEqual(len(filtered_attempts), 1)


class TestGetStudentExamAttempt(ExamsAPITestCase):
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

    def test_get_attempt(self):
        # check that fields match as expected (with only the needed keys)
        return 0

    def test_no_attempt(self):
        # check that None is returned if no attempt exists
        return 0


class TestGetExamByContentId(ExamsAPITestCase):
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

    def test_get_exam(self):
        # check that fields match
        return 0

    def test_no_exam(self):
        # check that none is returned
        return 0


class TestGetCurrentExamAttempt(ExamsAPITestCase):
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

    def test_get_attempt(self):
        # create two attempts
        # check that most recent is returned

        return 0

    def test_no_attempt(self):
        # check that none is returned
        return 0


class TestGetExamURLPath(ExamsAPITestCase):
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

    def test_get_exam_url(self):
        # assert that url structure is as expected

        return 0
