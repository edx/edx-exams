"""
Tests for API utility functions
"""
import uuid
from datetime import datetime, timedelta
from itertools import product

import ddt
from django.conf import settings
from django.utils import timezone
from freezegun import freeze_time
from opaque_keys.edx.keys import CourseKey, UsageKey

from edx_exams.apps.api.test_utils import ExamsAPITestCase
from edx_exams.apps.core.api import (
    check_if_exam_timed_out,
    create_exam_attempt,
    get_attempt_by_id,
    get_current_exam_attempt,
    get_exam_attempt_time_remaining,
    get_exam_by_content_id,
    get_exam_url_path,
    get_latest_attempt_for_user,
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
class TestCheckIfExamTimedOut(ExamsAPITestCase):
    """
    Tests for API utility function `check_if_exam_timed_out`
    """

    def setUp(self):
        super().setUp()

        self.course_id = 'course-v1:edx+test+f19'
        self.content_id = 'block-v1:edX+test+2023+type@sequential+block@1111111111'

        self.exam = Exam.objects.create(
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id=self.content_id,
            exam_name='test_exam',
            exam_type='proctored',
            time_limit_mins=60,
            due_date='3000-07-01 00:00:00',
            hide_after_due=False,
            is_active=True
        )

        self.one_hour_ago = timezone.now() - timedelta(hours=1)

    def create_mock_attempt(self, status, start_time, allowed_time_limit_mins):
        return ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1,
            status=status,
            start_time=start_time,
            allowed_time_limit_mins=allowed_time_limit_mins
        )

    @ddt.data(
        (ExamAttemptStatus.started, timezone.now() - timedelta(hours=1)),  # in progress and timed out
        (ExamAttemptStatus.ready_to_submit, timezone.now() - timedelta(hours=1)),
    )
    @ddt.unpack
    def test_submit_on_timeout(self, status, start_time):
        """
        Test that an attempt is returned when an in-progress exam times out
        """
        exam_attempt = self.create_mock_attempt(status, start_time, 60)
        self.assertEqual(check_if_exam_timed_out(exam_attempt), exam_attempt)

    @ddt.data(
        (ExamAttemptStatus.created, timezone.now() - timedelta(hours=1)),  # not in progress, but timed out
        (ExamAttemptStatus.submitted, timezone.now() - timedelta(hours=1)),
        (ExamAttemptStatus.started, timezone.now()),  # in progress, but not timed out
        (ExamAttemptStatus.ready_to_submit, timezone.now() - timedelta(minutes=59)),
        (ExamAttemptStatus.verified, timezone.now() - timedelta(minutes=30))  # neither in progress, nor timed out
    )
    @ddt.unpack
    def test_do_not_submit(self, status, start_time):
        """
        Test that None is returned when an exam is not in-progress or not timed out
        """
        exam_attempt = self.create_mock_attempt(status, start_time, 60)
        self.assertEqual(exam_attempt, check_if_exam_timed_out(exam_attempt))

    def test_missing_data(self):
        """
        Test that an exam attempt without a start time or
        time limit returns None
        """
        exam_attempt = self.create_mock_attempt(ExamAttemptStatus.created, None, 60)  # Has missing start_time
        self.assertEqual(exam_attempt, check_if_exam_timed_out(exam_attempt))


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

    def test_cannot_start_if_other_attempts_active(self):
        """
        Test that you cannot start another exam attempt if one is already active
        """
        # Already active exam attempt
        ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1,
            status=ExamAttemptStatus.started,
        )
        with self.assertRaises(ExamIllegalStatusTransition) as exc:
            update_attempt_status(self.exam_attempt.id, ExamAttemptStatus.started)
        self.assertIn('another exam attempt is currently active!', str(exc.exception))


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
        self.assertEqual(attempt, self.exam_attempt)

    def test_with_no_attempt(self):
        """
        Test that if the attempt does not exist, None is returned
        """
        self.assertIsNone(get_attempt_by_id(111111111))


@ddt.ddt
class TestGetLatestAttemptForUser(ExamsAPITestCase):
    """
    Test for the API utility function `get_latest_attempt_for_user`
    """

    def setUp(self):
        super().setUp()

        self.course_id = 'course-v1:edx+test+f19'
        self.content_id = '11111111'

        self.exam = Exam.objects.create(
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id=self.content_id,
            exam_name='test_exam',
            exam_type='proctored',
            time_limit_mins=30,
            due_date='2040-07-01 00:00:00',
            hide_after_due=False,
            is_active=True
        )

    def create_mock_attempt(self, user, status, start_time):
        return ExamAttempt.objects.create(
            user=user,
            exam=self.exam,
            attempt_number=1,
            status=status,
            start_time=start_time,
            allowed_time_limit_mins=None
        )

    def test_get_latest_exam_attempt_for_user(self):
        """
        Test that the GET function in the ExamAttempt view returns
        the latest exam attempt for a user
        """

        one_hour_ago = datetime.now() - timedelta(hours=1)
        expected_attempt = self.create_mock_attempt(self.user, ExamAttemptStatus.started, datetime.now())
        self.create_mock_attempt(self.user, ExamAttemptStatus.started, one_hour_ago)
        latest_attempt = get_latest_attempt_for_user(self.user.id)

        self.assertEqual(latest_attempt.status, expected_attempt.status)
        self.assertEqual(latest_attempt.attempt_number, expected_attempt.attempt_number)
        self.assertEqual(latest_attempt.user.username, expected_attempt.user.username)
        self.assertEqual(latest_attempt.exam.content_id, expected_attempt.exam.content_id)

    def test_no_attempt_for_user(self):
        """
        Test that if the user has no exam attempts, that the endpoint returns None
        """

        self.create_mock_attempt(self.user, ExamAttemptStatus.created, datetime.now())

        self.assertIsNone(get_latest_attempt_for_user(9999999999))

    def test_no_attempts_have_start_time(self):
        """
        Test that is the user has no exam attempts with a start time, that the endpoint returns None
        """
        self.create_mock_attempt(self.user, ExamAttemptStatus.created, None)

        self.assertIsNone(get_latest_attempt_for_user(self.user.id))


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
        Test that a non existent exam raises an error
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

    def test_exam_with_no_due_date(self):
        """
        Test that you can create an attempt for an exam with no due date
        """
        exam_id = self.exam.id
        user_id = self.user.id

        create_exam_attempt(exam_id, user_id)
        self.assertIsNotNone(ExamAttempt.objects.get(user_id=user_id, exam_id=exam_id))


class TestGetExamByContentId(ExamsAPITestCase):
    """
    Tests for the API utility function `get_exam_by_content_id`
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
            is_active=True,
        )
        Exam.objects.create(  # Inactive exam
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id='abcd1234',
            exam_name='test_exam',
            exam_type='proctored',
            time_limit_mins=30,
            is_active=False,
        )

    def test_get_exam(self):
        exam = get_exam_by_content_id(self.exam.course_id, self.exam.content_id)
        self.assertEqual(self.exam, exam)

    def test_no_exam(self):
        data = get_exam_by_content_id(self.exam.course_id, 1111111)
        self.assertIsNone(data)


class TestGetCurrentExamAttempt(ExamsAPITestCase):
    """
    Tests for the API utility function `get_current_exam_attempt`
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

    def test_get_attempt(self):
        # create two attempts
        ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1,
            status=ExamAttemptStatus.error,
        )

        most_recent_attempt = ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=2,
            status=ExamAttemptStatus.created,
        )

        # check that most recently created is returned
        attempt = get_current_exam_attempt(self.user.id, self.exam.id)
        self.assertEqual(most_recent_attempt, attempt)

    def test_no_attempt(self):
        data = get_current_exam_attempt(self.user.id, self.exam.id)
        self.assertIsNone(data)


class TestGetExamURLPath(ExamsAPITestCase):
    """
    Tests for the API utility function `get_exam_url_path`
    """

    def test_get_exam_url(self):
        course_id = 'course-v1:edx+test+f19'
        content_id = 'block-v1:edX+test+2023+type@sequential+block@1111111111'

        usage_key = UsageKey.from_string(content_id)
        course_key = CourseKey.from_string(course_id)
        expected_string = f'{settings.LEARNING_MICROFRONTEND_URL}/course/{course_key}/{usage_key}'

        url = get_exam_url_path(course_id, content_id)
        self.assertEqual(expected_string, url)
