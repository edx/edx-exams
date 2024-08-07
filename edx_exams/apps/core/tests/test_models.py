""" Tests for core models. """

from django.test import TestCase
from django_dynamic_fixture import G
from social_django.models import UserSocialAuth

from edx_exams.apps.core.models import CourseExamConfiguration, Exam, StudentAllowance, User
from edx_exams.apps.core.test_utils.factories import (
    CourseExamConfigurationFactory,
    ExamFactory,
    ProctoringProviderFactory,
    StudentAllowanceFactory,
    UserFactory
)


class UserTests(TestCase):
    """ User model tests. """
    TEST_CONTEXT = {'foo': 'bar', 'baz': None}

    def test_access_token(self):
        user = G(User)
        self.assertIsNone(user.access_token)

        social_auth = G(UserSocialAuth, user=user)
        self.assertIsNone(user.access_token)

        access_token = 'My voice is my passport. Verify me.'
        social_auth.extra_data['access_token'] = access_token
        social_auth.save()
        self.assertEqual(user.access_token, access_token)

    def test_get_full_name(self):
        """ Test that the user model concatenates first and last name if the full name is not set. """
        full_name = 'George Costanza'
        user = G(User, full_name=full_name)
        self.assertEqual(user.get_full_name(), full_name)

        first_name = 'Jerry'
        last_name = 'Seinfeld'
        user = G(User, first_name=first_name, last_name=last_name)
        expected = '{first_name} {last_name}'.format(first_name=first_name, last_name=last_name)
        self.assertEqual(user.get_full_name(), expected)

        user = G(User, full_name=full_name, first_name=first_name, last_name=last_name)
        self.assertEqual(user.get_full_name(), full_name)


class CourseExamConfigurationTests(TestCase):
    """
    CourseExamConfiguration model tests.
    """

    def setUp(self):
        super().setUp()

        self.escalation_email = 'test1@example.com'
        self.config = CourseExamConfigurationFactory()

        for _ in range(3):
            ExamFactory(provider=self.config.provider)

    def test_create_or_update_no_provider_change(self):
        old_provider = self.config.provider

        CourseExamConfiguration.create_or_update(
            self.config.course_id,
            self.config.provider,
            self.escalation_email,
        )

        self.config.refresh_from_db()

        # Assert that no new model instances were created.
        num_configs = CourseExamConfiguration.objects.count()
        self.assertEqual(num_configs, 1)

        self.assertEqual(self.config.provider, old_provider)
        self.assertEqual(self.config.escalation_email, self.escalation_email)

    def test_create_or_update_no_provider(self):
        CourseExamConfiguration.create_or_update(
            self.config.course_id,
            None,
            self.escalation_email,
        )

        self.config.refresh_from_db()

        # Assert that no new model instances were created.
        num_configs = CourseExamConfiguration.objects.count()
        self.assertEqual(num_configs, 1)

        self.assertEqual(self.config.provider, None)
        self.assertEqual(self.config.escalation_email, None)

    def test_create_or_update_provider_change_and_sync(self):
        other_provider = ProctoringProviderFactory()

        previous_exams = set(Exam.objects.all())

        CourseExamConfiguration.create_or_update(
            self.config.course_id,
            other_provider,
            self.escalation_email,
        )

        all_exams = set(Exam.objects.all())
        new_exams = all_exams - previous_exams

        self.assertEqual(previous_exams <= all_exams, True)
        self.assertEqual(new_exams <= all_exams, True)
        self.assertEqual(new_exams.isdisjoint(previous_exams), True)

        for exam in previous_exams:
            exam.refresh_from_db()
            self.assertEqual(exam.is_active, False)

        for exam in new_exams:
            self.assertEqual(exam.is_active, True)
            self.assertEqual(exam.provider, other_provider)

    def test_create_or_update_new_config(self):
        other_course_id = 'course-v1:edX+Test+Test_Course2'
        CourseExamConfiguration.create_or_update(
            other_course_id,
            self.config.provider,
            self.escalation_email,
        )

        # Assert that one new model instance was created.
        num_configs = CourseExamConfiguration.objects.count()
        self.assertEqual(num_configs, 2)

        new_config = CourseExamConfiguration.objects.get(course_id=other_course_id)
        self.assertEqual(new_config.provider, self.config.provider)
        self.assertEqual(new_config.escalation_email, self.escalation_email)


class StudentAllowanceTests(TestCase):
    """
    StudentAllowance model tests.
    """

    def setUp(self):
        super().setUp()

        self.course_id = 'course-v1:edX+Test+Test_Course'
        self.exam = ExamFactory(course_id=self.course_id)

    def test_bulk_create_or_update(self):
        """
        Test bulk_create_or_update can create new allowances and update existing ones.
        """
        conflict_user = UserFactory()
        conflict_allowance = StudentAllowanceFactory(user=conflict_user, exam=self.exam, extra_time_mins=66)
        allowances = [
            StudentAllowance(user=conflict_user, exam=self.exam, extra_time_mins=19),
            StudentAllowance(user=UserFactory(), exam=self.exam, extra_time_mins=29),
            StudentAllowance(user=UserFactory(), exam=self.exam, extra_time_mins=39),
        ]

        self.assertEqual(StudentAllowance.objects.count(), 1)
        StudentAllowance.bulk_create_or_update(allowances)
        self.assertEqual(StudentAllowance.objects.count(), 3)
        conflict_allowance.refresh_from_db()
        self.assertEqual(conflict_allowance.extra_time_mins, 19)

    def test_get_allowance_for_user(self):
        user = UserFactory()
        user_2 = UserFactory()
        allowance = StudentAllowanceFactory(user=user, exam=self.exam)

        self.assertEqual(StudentAllowance.get_allowance_for_user(self.exam.id, user.id), allowance)
        self.assertIsNone(StudentAllowance.get_allowance_for_user(self.exam.id, user_2.id))

    def test_get_allowances_for_course(self):
        user = UserFactory()
        user_2 = UserFactory()
        exam_other_course = ExamFactory(course_id='course-v1:edX+Test+Test_Course_Other')
        allowance = StudentAllowanceFactory(user=user, exam=self.exam)
        allowance_2 = StudentAllowanceFactory(user=user_2, exam=self.exam)
        StudentAllowanceFactory(user=user, exam=exam_other_course)

        self.assertEqual(
            set(StudentAllowance.get_allowances_for_course(self.course_id)), set([allowance, allowance_2])
        )
