"""
Tests for the exams API views
"""
import json
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

import ddt
import pytz
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from token_utils.api import unpack_token_for

from edx_exams.apps.api.serializers import ExamSerializer, StudentAttemptSerializer
from edx_exams.apps.api.test_utils import ExamsAPITestCase
from edx_exams.apps.api.test_utils.factories import UserFactory
from edx_exams.apps.core.exam_types import get_exam_type
from edx_exams.apps.core.exceptions import ExamAttemptOnPastDueExam, ExamIllegalStatusTransition
from edx_exams.apps.core.models import CourseExamConfiguration, Exam, ExamAttempt, ProctoringProvider
from edx_exams.apps.core.statuses import ExamAttemptStatus


@ddt.ddt
class CourseExamsViewTests(ExamsAPITestCase):
    """
    Tests CourseExamsView
    """

    def setUp(self):
        super().setUp()

        self.course_id = 'course-v1:edx+test+f19'
        self.content_id = '11111111'

        self.course_exam_config = CourseExamConfiguration.objects.create(
            course_id=self.course_id,
            provider=self.test_provider,
            allow_opt_out=False
        )

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

        self.url = reverse('api:v1:exams-course_exams', kwargs={'course_id': self.course_id})

    def patch_api(self, user, data):
        """
        Helper function to make a patch request to the API
        """

        data = json.dumps(data)
        headers = self.build_jwt_headers(user)

        return self.client.patch(self.url, data, **headers, content_type="application/json")

    def get_response(self, user, data, expected_response):
        """
        Helper function to get API response
        """
        response = self.patch_api(user, data)
        self.assertEqual(response.status_code, expected_response)

        return response

    def test_auth_failures(self):
        """
        Verify the endpoint validates permissions
        """

        # Test unauthenticated
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, 401)

        # Test non-staff worker
        random_user = UserFactory()
        self.get_response(random_user, [], 403)

    def test_exam_empty_exam_list(self):
        """
        Test that exams not included in request are marked as inactive
        """
        course_exams = Exam.objects.filter(course_id=self.course_id)
        self.assertEqual(len(course_exams.filter(is_active=True)), 1)
        self.assertEqual(len(course_exams.filter(is_active=False)), 0)

        self.get_response(self.user, [], 200)

        course_exams = Exam.objects.filter(course_id=self.course_id)
        self.assertEqual(len(course_exams.filter(is_active=True)), 0)
        self.assertEqual(len(course_exams.filter(is_active=False)), 1)

    def test_invalid_data(self):
        """
        Assert that endpoint returns 400 if data does not pass serializer validation
        """
        data = [
            {
                'content_id': '22222222',
                'exam_name': 'Test Exam 2',
                'exam_type': 'timed',
                'time_limit_mins': 30,
                'due_date': '2025-07-01 00:00:00',
                'hide_after_due': 'xxxx',
                'is_active': 'yyyy',
            }
        ]
        response = self.get_response(self.user, data, 400)
        self.assertIn("hide_after_due", response.data["errors"][0])
        self.assertIn("is_active", response.data["errors"][0])

    def test_invalid_exam_type(self):
        """
        Test that endpoint returns 400 if exam type is invalid
        """
        data = [
            {
                'content_id': '22222222',
                'exam_name': 'Test Exam 2',
                'exam_type': 'something_bad',
                'time_limit_mins': 30,
                'due_date': '2025-07-01 00:00:00',
                'hide_after_due': False,
                'is_active': True,
            }
        ]
        response = self.get_response(self.user, data, 400)
        self.assertIn("exam_type", response.data["errors"][0])

    def test_existing_exam_update(self):
        """
        Test that an exam can be updated if it already exists
        """

        data = [
            {
                'content_id': self.exam.content_id,
                'exam_name': 'Something Different',
                'exam_type': self.exam.exam_type,  # exam type differs from existing exam
                'time_limit_mins': 45,
                'due_date': self.exam.due_date,
                'hide_after_due': self.exam.hide_after_due,
                'is_active': self.exam.is_active,
            }
        ]
        self.get_response(self.user, data, 200)

        exam = Exam.objects.get(course_id=self.course_id, content_id=self.content_id)
        self.assertEqual(exam.exam_name, 'Something Different')
        self.assertEqual(exam.provider, self.exam.provider)
        self.assertEqual(exam.time_limit_mins, 45)
        self.assertEqual(exam.due_date, pytz.utc.localize(datetime.fromisoformat(self.exam.due_date)))
        self.assertEqual(exam.hide_after_due, self.exam.hide_after_due)
        self.assertEqual(exam.is_active, self.exam.is_active)

    def test_exam_modified_type(self):
        """
        Test that when updating an exam to a different exam_type, the pre-existing exam
        is marked as inactive, and a new exam is created
        """
        data = [
            {
                'content_id': self.exam.content_id,
                'exam_name': self.exam.exam_name,
                'exam_type': 'timed',  # exam type differs from existing exam
                'time_limit_mins': 30,
                'due_date': self.exam.due_date,
                'hide_after_due': self.exam.hide_after_due,
                'is_active': True,
            }
        ]
        self.get_response(self.user, data, 200)

        # check that proctored exam has been marked as inactive
        proctored_exam = Exam.objects.get(course_id=self.course_id, content_id=self.content_id, exam_type='proctored')
        self.assertFalse(proctored_exam.is_active)

        # check that timed exam has been created
        timed_exam = Exam.objects.get(course_id=self.course_id, content_id=self.content_id, exam_type='timed')
        self.assertEqual(timed_exam.exam_name, self.exam.exam_name)
        self.assertEqual(timed_exam.provider, None)
        self.assertEqual(timed_exam.time_limit_mins, 30)
        self.assertEqual(timed_exam.due_date, pytz.utc.localize(datetime.fromisoformat(self.exam.due_date)))
        self.assertEqual(timed_exam.hide_after_due, self.exam.hide_after_due)
        self.assertEqual(timed_exam.is_active, True)

        # modify same exam back to proctored
        data = [
            {
                'content_id': self.exam.content_id,
                'exam_name': self.exam.exam_name,
                'exam_type': 'proctored',  # exam type differs from existing exam
                'time_limit_mins': 30,
                'due_date': self.exam.due_date,
                'hide_after_due': self.exam.hide_after_due,
                'is_active': True,
            }
        ]
        self.get_response(self.user, data, 200)

        # check that only two exams still exist (should not create a third)
        exams = Exam.objects.filter(course_id=self.course_id, content_id=self.content_id)
        self.assertEqual(len(exams), 2)

        # check that timed exam is marked inactive
        timed_exam = Exam.objects.get(course_id=self.course_id, content_id=self.content_id, exam_type='timed')
        self.assertFalse(timed_exam.is_active)

        # check that proctored exam data is correct
        proctored_exam = Exam.objects.get(course_id=self.course_id, content_id=self.content_id, exam_type='proctored')
        self.assertEqual(proctored_exam.exam_name, self.exam.exam_name)
        self.assertEqual(proctored_exam.provider, self.exam.provider)
        self.assertEqual(proctored_exam.time_limit_mins, 30)
        self.assertEqual(proctored_exam.due_date, pytz.utc.localize(datetime.fromisoformat(self.exam.due_date)))
        self.assertEqual(proctored_exam.hide_after_due, self.exam.hide_after_due)
        self.assertEqual(proctored_exam.is_active, True)

    @ddt.data(
        (False, 'proctored', False),  # test case for a proctored exam with a course config
        (False, 'timed', True),  # test case for a timed exam with a course config
    )
    @ddt.unpack
    def test_exams_config(self, other_course_id, exam_type, expect_none_provider):
        """
        Test that the correct provider is set for a new exam based on the course's exam config
        """
        course_id = 'courses-v1:edx+testing2+2022' if other_course_id else self.course_id
        provider = None if expect_none_provider else self.test_provider

        data = [
            {
                'content_id': '22222222',
                'exam_name': 'Test Exam 2',
                'exam_type': exam_type,
                'time_limit_mins': 30,
                'due_date': '2025-07-01 00:00:00',
                'hide_after_due': False,
                'is_active': True,
            }
        ]

        self.url = reverse('api:v1:exams-course_exams', kwargs={'course_id': course_id})
        self.get_response(self.user, data, 200)

        self.assertEqual(len(Exam.objects.filter(course_id=self.course_id)), 1 if other_course_id else 2)
        new_exam = Exam.objects.get(content_id='22222222')
        self.assertEqual(new_exam.exam_name, 'Test Exam 2')
        self.assertEqual(new_exam.exam_type, exam_type)
        self.assertEqual(new_exam.provider, provider)
        self.assertEqual(new_exam.time_limit_mins, 30)
        self.assertEqual(new_exam.due_date, pytz.utc.localize(datetime.fromisoformat('2025-07-01 00:00:00')))
        self.assertEqual(new_exam.hide_after_due, False)
        self.assertEqual(new_exam.is_active, True)


@ddt.ddt
class CourseExamConfigurationsViewTests(ExamsAPITestCase):
    """
    Test CourseExamConfigurationsView
    """

    def setUp(self):
        super().setUp()

        self.course_id = 'course-v1:edx+test+f19'

        self.url = reverse('api:v1:course-exam-config', kwargs={'course_id': self.course_id})

    def patch_api(self, user, data):
        """
        Helper function to make patch request to the API
        """

        data = json.dumps(data)
        headers = self.build_jwt_headers(user)

        return self.client.patch(self.url, data, **headers, content_type="application/json")

    def test_patch_auth_failures(self):
        """
        Verify the endpoint validates permissions
        """
        # Test unauthenticated
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, 401)

        # Test non-staff user
        random_user = UserFactory()
        response = self.patch_api(random_user, {})
        self.assertEqual(403, response.status_code)

    def test_patch_invalid_data(self):
        """
        Assert that endpoint returns 400 if provider is missing
        """
        data = {}

        response = self.patch_api(self.user, data)
        self.assertEqual(400, response.status_code)

    def test_patch_invalid_provider(self):
        """
        Assert endpoint returns 400 if provider is invalid
        """
        data = {'provider': 'nonexistent_provider'}

        response = self.patch_api(self.user, data)
        self.assertEqual(400, response.status_code)

    def test_patch_config_update(self):
        """
        Test that config is updated
        """
        CourseExamConfiguration.objects.create(
            course_id=self.course_id,
            provider=self.test_provider,
        )
        provider = ProctoringProvider.objects.create(
            name='test_provider_2',
            verbose_name='testing_provider_2',
            lti_configuration_id='223456789'
        )
        data = {'provider': provider.name}

        response = self.patch_api(self.user, data)
        self.assertEqual(204, response.status_code)
        self.assertEqual(len(CourseExamConfiguration.objects.all()), 1)

        config = CourseExamConfiguration.get_configuration_for_course(self.course_id)
        self.assertEqual(config.provider, provider)

    def test_patch_config_update_exams(self):
        """
        Test that config is updated
        """
        CourseExamConfiguration.objects.create(
            course_id=self.course_id,
            provider=self.test_provider,
        )
        provider = ProctoringProvider.objects.create(
            name='test_provider_2',
            verbose_name='testing_provider_2',
            lti_configuration_id='223456789'
        )
        Exam.objects.create(
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id='11111',
            exam_name='test_exam1',
            exam_type='proctored',
            time_limit_mins=30,
            due_date='2021-07-01 00:00:00',
            hide_after_due=False,
            is_active=True
        )
        Exam.objects.create(
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id='22222',
            exam_name='test_exam2',
            exam_type='proctored',
            time_limit_mins=30,
            due_date='2021-07-01 00:00:00',
            hide_after_due=False,
            is_active=True
        )
        exams = Exam.objects.filter(course_id=self.course_id, is_active=True)
        self.assertEqual(2, len(exams))

        data = {'provider': provider.name}
        response = self.patch_api(self.user, data)
        self.assertEqual(204, response.status_code)
        self.assertEqual(len(CourseExamConfiguration.objects.all()), 1)
        config = CourseExamConfiguration.get_configuration_for_course(self.course_id)
        self.assertEqual(config.provider, provider)

        exams = Exam.objects.filter(course_id=self.course_id, is_active=True)
        self.assertEqual(2, len(exams))
        for exam in exams:
            self.assertEqual(provider, exam.provider)

        inactive_exams = Exam.objects.filter(course_id=self.course_id, is_active=False)
        self.assertEqual(2, len(inactive_exams))
        for exam in inactive_exams:
            self.assertEqual(self.test_provider, exam.provider)

        # updating to the same provider is a do nothing, no new exams
        data = {'provider': provider.name}
        response = self.patch_api(self.user, data)
        self.assertEqual(204, response.status_code)
        self.assertEqual(len(CourseExamConfiguration.objects.all()), 1)
        config = CourseExamConfiguration.get_configuration_for_course(self.course_id)
        self.assertEqual(config.provider, provider)

        exams = Exam.objects.filter(course_id=self.course_id, is_active=True)
        self.assertEqual(2, len(exams))
        for exam in exams:
            self.assertEqual(provider, exam.provider)

        inactive_exams = Exam.objects.filter(course_id=self.course_id, is_active=False)
        self.assertEqual(2, len(inactive_exams))
        for exam in inactive_exams:
            self.assertEqual(self.test_provider, exam.provider)

        # updating back to the original provider creates two new active exams, now 4 inactive
        data = {'provider': self.test_provider.name}
        response = self.patch_api(self.user, data)
        self.assertEqual(204, response.status_code)
        self.assertEqual(len(CourseExamConfiguration.objects.all()), 1)
        config = CourseExamConfiguration.get_configuration_for_course(self.course_id)
        self.assertEqual(config.provider, self.test_provider)

        exams = Exam.objects.filter(course_id=self.course_id, is_active=True)
        self.assertEqual(2, len(exams))
        for exam in exams:
            self.assertEqual(self.test_provider, exam.provider)

        inactive_exams = Exam.objects.filter(course_id=self.course_id, is_active=False)
        self.assertEqual(4, len(inactive_exams))

    def test_patch_config_create(self):
        """
        Test that config is created
        """
        data = {'provider': 'test_provider'}

        response = self.patch_api(self.user, data)
        self.assertEqual(204, response.status_code)
        self.assertEqual(len(CourseExamConfiguration.objects.all()), 1)

        config = CourseExamConfiguration.get_configuration_for_course(self.course_id)
        self.assertEqual(config.provider, self.test_provider)

    def test_patch_null_provider(self):
        """
        Assert provider can be explicitly set to null
        """
        data = {'provider': None}

        response = self.patch_api(self.user, data)
        self.assertEqual(204, response.status_code)
        self.assertEqual(len(CourseExamConfiguration.objects.all()), 1)

        config = CourseExamConfiguration.get_configuration_for_course(self.course_id)
        self.assertEqual(config.provider, None)

    def test_get_config(self):
        """
        Non-staff users can get course configuration
        """
        CourseExamConfiguration.objects.create(
            course_id=self.course_id,
            provider=self.test_provider
        )
        nonstaff_user = UserFactory()
        headers = self.build_jwt_headers(nonstaff_user)
        response = self.client.get(self.url, **headers)
        self.assertEqual(200, response.status_code)
        self.assertEqual('test_provider', response.data.get('provider'))

    def test_get_missing_config(self):
        """
        Returns null values if no configuration exists
        """
        nonstaff_user = UserFactory()
        headers = self.build_jwt_headers(nonstaff_user)
        response = self.client.get(self.url, **headers)
        self.assertEqual(200, response.status_code)
        self.assertIsNone(response.data.get('provider'))


class ProctoringProvidersViewTest(ExamsAPITestCase):
    """
    Tests ProctoringProvidersView
    """

    def get_response(self):
        """
        Helper function to make a get request
        """
        url = reverse("api:v1:proctoring-providers-list")
        response = self.client.get(url)
        return response

    def test_proctoring_providers_list(self):
        test_provider2 = ProctoringProvider.objects.create(
            name='test_provider2',
            verbose_name='testing_provider2',
            lti_configuration_id='223456789'
        )
        response = self.get_response()
        response_data_list = []

        for item in response.data:
            response_data_list.append(item['name'])

        response_data_list.sort()

        self.assertEqual(response.status_code, 200)
        self.assertIn(response_data_list[0], self.test_provider.name)
        self.assertIn(response_data_list[1], test_provider2.name)

    def test_proctoring_providers_list_empty(self):

        self.test_provider.delete()

        response = self.get_response()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)


@ddt.ddt
class ExamAccessTokensViewsTests(ExamsAPITestCase):
    """
    Tests for Exam Access Token Views.
    """

    def setUp(self):
        super().setUp()

        self.course_id = 'course-v1:edx+test+f19'

        self.due_date = timezone.now() + timedelta(minutes=5)
        self.exam = Exam.objects.create(
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id='abcd1234',
            exam_name='test_exam',
            exam_type='proctored',
            time_limit_mins=30,
            due_date=self.due_date,
            hide_after_due=False,
            is_active=True
        )
        self.exam_id = self.exam.id
        self.url = reverse('api:v1:exam-access-tokens', kwargs={'exam_id': self.exam_id})

        self.past_due_date = timezone.now() - timedelta(minutes=5)
        self.past_due_exam = Exam.objects.create(
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id='abcd1234',
            exam_name='test_exam',
            exam_type='proctored',
            time_limit_mins=30,
            due_date=self.past_due_date,
            hide_after_due=False,
            is_active=True
        )

        self.past_due_exam_id = self.past_due_exam.id
        self.past_due_url = reverse('api:v1:exam-access-tokens', kwargs={'exam_id': self.past_due_exam_id})

    def get_exam_access(self, user, url):
        """
        Helper function to make a get request
        """
        headers = self.build_jwt_headers(user)
        return self.client.get(url, **headers)

    def assert_valid_exam_access_token(self, response, user, exam):
        token = response.cookies["exam_access_token"].value
        self.assertEqual(unpack_token_for(token, user.lms_user_id).get('course_id'), exam.course_id)
        self.assertEqual(unpack_token_for(token, user.lms_user_id).get('content_id'), exam.content_id)

    def test_auth_failures(self):
        """
        Verify the endpoint validates permissions
        """
        # Test unauthenticated
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_exam_not_found(self):
        """
        Verify the endpoint returns 404 if exam is not found
        """
        url = reverse('api:v1:exam-access-tokens', kwargs={'exam_id': 674})

        headers = self.build_jwt_headers(self.user)
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 404)

    def test_access_not_granted(self):
        """
        Verify the endpoint doesn't grant access for an exam
        without an existing exam attempt or past due date.
        """
        response = self.get_exam_access(self.user, self.url)
        self.assertEqual(403, response.status_code)

    @ddt.data(
        (False, 'started', 200),
        (False, 'created', 403),
        (True, 'verified', 200),
        (True, 'created', 403),
    )
    @ddt.unpack
    def test_access_granted_started_exam_attempt(self, exam_past_due, attempt_status, response_status):
        """
        Verify the endpoint grants/doesn't grant access for an exam
        based on the status of the exam attempt.
        """
        exam = self.past_due_exam if exam_past_due else self.exam
        due_date = self.past_due_date if exam_past_due else self.due_date

        allowed_time_limit_mins = exam.time_limit_mins
        start_time = due_date - timedelta(minutes=allowed_time_limit_mins/2)
        ExamAttempt.objects.create(
            user=self.user,
            exam=exam,
            attempt_number=1,
            status=attempt_status,
            start_time=start_time,
            allowed_time_limit_mins=allowed_time_limit_mins
        )

        url = reverse('api:v1:exam-access-tokens', kwargs={'exam_id': exam.id})
        response = self.get_exam_access(self.user, url)
        self.assertEqual(response_status, response.status_code)
        if response_status == 200:
            self.assert_valid_exam_access_token(response, self.user, exam)

    def test_access_not_granted_started_exam_attempt_missing_start_time(self):
        """
        Verify the endpoint does not grant access for an exam
        with an existing, started exam attempt that is missing start_time.
        """
        allowed_time_limit_mins = self.exam.time_limit_mins
        ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1,
            status='started',
            allowed_time_limit_mins=allowed_time_limit_mins
        )

        response = self.get_exam_access(self.user, self.url)
        self.assertEqual(403, response.status_code)

    @ddt.data(
        ('started', 200),
        ('created', 403),
    )
    @ddt.unpack
    def test_access_no_due_date(self, attempt_status, response_status):
        """
        Verify the endpoint grants access for an exam
        with no due date, if started exam attempt.
        """
        no_due_date_exam = Exam.objects.create(
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id='abcd1234',
            exam_name='test_exam',
            exam_type='proctored',
            time_limit_mins=30,
            hide_after_due=False,
            is_active=True
        )

        no_due_date_exam_id = no_due_date_exam.id
        no_due_date_url = reverse('api:v1:exam-access-tokens', kwargs={'exam_id': no_due_date_exam_id})

        allowed_time_limit_mins = no_due_date_exam.time_limit_mins
        start_time = timezone.now() - timedelta(minutes=allowed_time_limit_mins/2)
        ExamAttempt.objects.create(
            user=self.user,
            exam=no_due_date_exam,
            attempt_number=1,
            status=attempt_status,
            start_time=start_time,
            allowed_time_limit_mins=allowed_time_limit_mins
        )

        response = self.get_exam_access(self.user, no_due_date_url)
        self.assertEqual(response_status, response.status_code)
        if response_status == 200:
            self.assert_valid_exam_access_token(response, self.user, no_due_date_exam)

    def test_access_not_granted_if_hide_after_due(self):
        """
        Verify the endpoint does not grant access for past-due exam
        when the exam is set to hide after due.
        """
        past_due_exam_hide = Exam.objects.create(
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id='abcd1234',
            exam_name='test_exam',
            exam_type='proctored',
            time_limit_mins=30,
            due_date=self.past_due_date,
            hide_after_due=True,
            is_active=True
        )

        past_due_exam_id = past_due_exam_hide.id
        past_due_url = reverse('api:v1:exam-access-tokens', kwargs={'exam_id': past_due_exam_id})

        start_time = self.past_due_date - timedelta(minutes=60)
        allowed_time_limit_mins = past_due_exam_hide.time_limit_mins
        ExamAttempt.objects.create(
            user=self.user,
            exam=past_due_exam_hide,
            attempt_number=1,
            status='verified',
            start_time=start_time,
            allowed_time_limit_mins=allowed_time_limit_mins
        )

        response = self.get_exam_access(self.user, past_due_url)
        self.assertEqual(403, response.status_code)

    def test_access_not_granted_no_status_exam_attempt(self):
        """
        Verify the endpoint does not grant access for an exam
        with an existing exam attempt that is not started.
        """
        start_time = self.due_date - timedelta(minutes=60)
        allowed_time_limit_mins = self.exam.time_limit_mins
        ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1,
            start_time=start_time,
            allowed_time_limit_mins=allowed_time_limit_mins
        )

        response = self.get_exam_access(self.user, self.url)
        self.assertEqual(403, response.status_code)

    @ddt.data(
        (timedelta(minutes=35), timedelta(minutes=0), 403),  # exam attempt with zero time remaining
        (timedelta(minutes=10), timedelta(minutes=10), 403),  # exam attempt that is past due date
        (timedelta(minutes=20), timedelta(minutes=0), 200),  # exam attempt time remaining less than due date
    )
    @ddt.unpack
    def test_access_granted_started_exam_attempt_various_times(self, start_delta, current_time_delta, response_status):
        """
        Verify the endpoint grants access for an exam
        with an existing exam attempt.
        """

        # freeze time adding the delta to the due_date, this way we can manipulate if the due date has actually passed
        with freeze_time(timezone.now() + current_time_delta):
            start_time = self.due_date - start_delta
            allowed_time_limit_mins = self.exam.time_limit_mins
            ExamAttempt.objects.create(
                user=self.user,
                exam=self.exam,
                attempt_number=1,
                status='started',
                start_time=start_time,
                allowed_time_limit_mins=allowed_time_limit_mins
            )

            response = self.get_exam_access(self.user, self.url)
        self.assertEqual(response_status, response.status_code)
        if response_status == 200:
            self.assert_valid_exam_access_token(response, self.user, self.exam)

    def test_access_granted_past_due_exam_no_attempt(self):
        """
        Verify the endpoint grants access for an exam
        with no existing attempt that is past due.
        """
        response = self.get_exam_access(self.user, self.past_due_url)
        self.assertEqual(200, response.status_code)
        self.assert_valid_exam_access_token(response, self.user, self.past_due_exam)


@ddt.ddt
class ExamAttemptViewTest(ExamsAPITestCase):
    """
    Tests ExamAttemptView
    """

    def setUp(self):
        super().setUp()

        self.course_id = 'course-v1:edx+test+f19'
        self.content_id = '11111111'

        self.course_exam_config = CourseExamConfiguration.objects.create(
            course_id=self.course_id,
            provider=self.test_provider,
            allow_opt_out=False
        )

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

        self.non_staff_user = UserFactory()

    def put_api(self, user, attempt_id, data):
        """
        Helper function to make patch request to the API
        """

        data = json.dumps(data)
        headers = self.build_jwt_headers(user)
        url = reverse('api:v1:exams-attempt', args=[attempt_id])

        return self.client.put(url, data, **headers, content_type="application/json")

    def post_api(self, user, data):
        """
        Helper function to make post request to the API
        """
        data = json.dumps(data)
        headers = self.build_jwt_headers(user)
        url = reverse('api:v1:exams-attempt')

        return self.client.post(url, data, **headers, content_type="application/json")

    def test_put_user_update_permissions(self):
        """
        Test that non-staff users cannot update the attempt of another user
        """
        # create non-staff user with attempt
        other_user = UserFactory()
        attempt = ExamAttempt.objects.create(
            user=other_user,
            exam=self.exam,
            attempt_number=1111111,
            status=ExamAttemptStatus.created,
            start_time=None,
            allowed_time_limit_mins=None,
        )

        # try to update other user's attempt
        response = self.put_api(self.non_staff_user, attempt.id, {'action': 'start'})
        self.assertEqual(response.status_code, 403)

    def test_put_attempt_does_not_exist(self):
        """
        Test that updating an attempt that does not exist fails
        """
        response = self.put_api(self.non_staff_user, 111111111, {'action': 'start'})
        self.assertEqual(response.status_code, 400)

    @ddt.data(
        ('start', ExamAttemptStatus.started),
        ('stop', ExamAttemptStatus.ready_to_submit),
        ('submit', ExamAttemptStatus.submitted),
        ('click_download_software', ExamAttemptStatus.download_software_clicked),
        ('error', ExamAttemptStatus.error),
    )
    @ddt.unpack
    @patch('edx_exams.apps.api.v1.views.update_attempt_status')
    def test_put_update_exam_attempt(self, action, expected_status, mock_update_attempt_status):
        """
        Test that an exam can be updated
        """
        # create exam attempt for user
        attempt = ExamAttempt.objects.create(
            user=self.non_staff_user,
            exam=self.exam,
            attempt_number=1111111,
            status=ExamAttemptStatus.created,
            start_time=None,
            allowed_time_limit_mins=None,
        )

        mock_update_attempt_status.return_value = attempt.id

        response = self.put_api(self.non_staff_user, attempt.id, {'action': action})
        self.assertEqual(response.status_code, 200)
        mock_update_attempt_status.assert_called_once_with(attempt.id, expected_status)

    @patch('edx_exams.apps.api.v1.views.update_attempt_status')
    def test_put_exception_raised(self, mock_update_attempt_status):
        """
        Test that if an exception is raised, endpoint returns 400 with error message
        """
        error_msg = 'Something bad happened'
        mock_update_attempt_status.side_effect = ExamIllegalStatusTransition(error_msg)

        attempt = ExamAttempt.objects.create(
            user=self.non_staff_user,
            exam=self.exam,
            attempt_number=1111111,
            status=ExamAttemptStatus.created,
            start_time=None,
            allowed_time_limit_mins=None,
        )

        response = self.put_api(self.non_staff_user, attempt.id, {'action': 'start'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(error_msg, response.data['detail'])

    def test_put_invalid_action(self):
        """
        Test that an unrecognized action fails
        """

        attempt = ExamAttempt.objects.create(
            user=self.non_staff_user,
            exam=self.exam,
            attempt_number=1111111,
            status=ExamAttemptStatus.started,
            start_time='2020-07-01 00:00:00',
            allowed_time_limit_mins=None,
        )

        # try to update other user's attempt
        response = self.put_api(self.non_staff_user, attempt.id, {'action': 'junk'})
        self.assertEqual(response.status_code, 400)
        # check that error message is specific to starting an attempt
        self.assertIn('Unrecognized action', response.data['detail'])

    @patch('edx_exams.apps.api.v1.views.create_exam_attempt')
    def test_post_exception_raised(self, mock_create_attempt):
        """
        Test that endpoint returns 400 if exception is raised
        """
        error_msg = 'Something bad happened'
        mock_create_attempt.side_effect = ExamAttemptOnPastDueExam(error_msg)

        data = {
            'start_clock': 'false',
            'exam_id': self.exam.id,
        }
        response = self.post_api(self.non_staff_user, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(error_msg, response.data['detail'])

    @ddt.data(
        True,
        False,
    )
    @patch('edx_exams.apps.api.v1.views.create_exam_attempt')
    @patch('edx_exams.apps.api.v1.views.update_attempt_status')
    def test_post_create_attempt(self, start_immediately, mock_update_attempt, mock_create_attempt):
        """
        Test that an exam attempt can be created
        """
        mock_attempt_id = 1111111
        mock_create_attempt.return_value = mock_attempt_id
        mock_update_attempt.return_value = mock_attempt_id

        data = {
            'start_clock': str(start_immediately).lower(),
            'exam_id': self.exam.id,
        }

        response = self.post_api(self.non_staff_user, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['exam_attempt_id'], mock_attempt_id)

        mock_create_attempt.assert_called_once_with(self.exam.id, self.non_staff_user.id)

        if start_immediately:
            mock_update_attempt.assert_called_once_with(mock_attempt_id, ExamAttemptStatus.started)


class CourseExamAttemptViewTest(ExamsAPITestCase):
    """
    Tests CourseExamAttemptView
    """

    def setUp(self):
        super().setUp()

        self.course_id = 'course-v1:edx+test+f19'
        self.content_id = 'block-v1:edX+test+2023+type@sequential+block@1111111111'

        self.course_exam_config = CourseExamConfiguration.objects.create(
            course_id=self.course_id,
            provider=self.test_provider,
            allow_opt_out=False
        )

        self.exam = Exam.objects.create(
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id=self.content_id,
            exam_name='test_exam',
            exam_type='proctored',
            time_limit_mins=30,
            due_date='2040-07-01T00:00:00Z',
            hide_after_due=False,
            is_active=True
        )

    def get_api(self, user, course_id, content_id):
        """
        Helper function to make patch request to the API
        """

        headers = self.build_jwt_headers(user)
        url = reverse(
            'api:v1:student-course_exam_attempt',
            kwargs={'course_id': course_id, 'content_id': content_id}
        )

        return self.client.get(url, **headers)

    def test_no_exam(self):
        """
        Test endpoint for a content ID that doesn't exist
        """
        response = self.get_api(self.user, self.course_id, '1111111')
        self.assertEqual(response.data['exam'], {})

    def test_no_active_attempt(self):
        """
        Test endpoint for an existing exam, but no attempt for user
        """
        exam_type_class = get_exam_type(self.exam.exam_type)
        expected_data = ExamSerializer(self.exam).data
        expected_data['type'] = self.exam.exam_type
        expected_data['is_proctored'] = exam_type_class.is_proctored
        expected_data['is_practice_exam'] = exam_type_class.is_practice
        expected_data['backend'] = self.exam.provider.verbose_name
        expected_data['attempt'] = {}

        response = self.get_api(self.user, self.course_id, self.content_id)
        response_exam = response.data['exam']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_exam, expected_data)

    def test_active_attempt(self):
        """
        Test that if attempt exists, it is returned as part of the exam object
        """
        attempt = ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1,
            status=ExamAttemptStatus.created,
        )
        serialized_attempt = StudentAttemptSerializer(attempt).data

        response = self.get_api(self.user, self.course_id, self.content_id)

        self.assertEqual(response.status_code, 200)
        response_exam = response.data['exam']

        self.assertEqual(response_exam['attempt'], serialized_attempt)
