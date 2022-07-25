"""
Tests for the exams API views
"""
import json
import uuid
from datetime import datetime

import ddt
import pytz
from django.urls import reverse

from edx_exams.apps.api.test_utils import ExamsAPITestCase
from edx_exams.apps.api.test_utils.factories import UserFactory
from edx_exams.apps.core.models import CourseExamConfiguration, Exam, ProctoringProvider


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
        (True, 'proctored', True),  # test case for a proctored exam with no course config
        (False, 'proctored', False),  # test case for a proctored exam with a course config
        (False, 'timed', True),  # test case for a timed exam with a course config
        (True, 'timed', True)  # test case for a timed exam with no course config
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

    def test_auth_failures(self):
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

    def test_invalid_data(self):
        """
        Assert that endpoint returns 400 if provider is missing
        """
        data = {}

        response = self.patch_api(self.user, data)
        self.assertEqual(400, response.status_code)

    def test_invalid_provider(self):
        """
        Assert endpoint returns 400 if provider is invalid
        """
        data = {'provider': 'nonexistent_provider'}

        response = self.patch_api(self.user, data)
        self.assertEqual(400, response.status_code)

    def test_config_update(self):
        """
        Test that config is updated
        """
        CourseExamConfiguration.objects.create(
            course_id=self.course_id,
            provider=self.test_provider
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

        config = CourseExamConfiguration.objects.get(course_id=self.course_id)
        self.assertEqual(config.provider, provider)

    def test_config_create(self):
        """
        Test that config is created
        """
        data = {'provider': 'test_provider'}

        response = self.patch_api(self.user, data)
        self.assertEqual(204, response.status_code)
        self.assertEqual(len(CourseExamConfiguration.objects.all()), 1)

        config = CourseExamConfiguration.objects.get(course_id=self.course_id)
        self.assertEqual(config.provider, self.test_provider)


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
        proctoring_providers_list = ProctoringProvider.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(proctoring_providers_list), 2)
        self.assertIn(self.test_provider, proctoring_providers_list)
        self.assertIn(test_provider2, proctoring_providers_list)

    def test_proctoring_providers_list_empty(self):

        self.test_provider.delete()

        response = self.get_response()
        proctoring_providers_list = ProctoringProvider.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(proctoring_providers_list), 0)
