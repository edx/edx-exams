""" Tests for edx-proctoring override views """
import json
import uuid
from posixpath import join as urljoin
from unittest.mock import Mock

import ddt
import mock
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from requests.exceptions import HTTPError
from requests.models import Response
from responses import matchers
from rest_framework.exceptions import ValidationError

from edx_exams.apps.api.test_utils import ExamsAPITestCase
from edx_exams.apps.api.test_utils.factories import UserFactory
from edx_exams.apps.core.models import CourseExamConfiguration, Exam
from edx_exams.apps.router.views import CourseExamsLegacyView


@ddt.ddt
class CourseExamsLegacyViewTest(ExamsAPITestCase):
    """ Tests for exam registration endpoints """

    def setUp(self):
        super().setUp()

        self.course_id = 'course-v1:edx+test+f19'
        self.url = reverse('api:v1:exams-course_exams', kwargs={'course_id': self.course_id})

        self.exam = Exam.objects.create(
            resource_id=str(uuid.uuid4()),
            course_id=self.course_id,
            provider=self.test_provider,
            content_id='abcd1234',
            exam_name='test_exam',
            exam_type='proctored',
            time_limit_mins=30,
            due_date='2021-07-01 00:00:00',
            hide_after_due=False,
            is_active=True
        )

    def test_auth_failures(self):
        """
        Verify the endpoint validates permissions
        """

        # Test unauthenticated
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, 401)

        # Test non-staff worker
        random_user = UserFactory()
        response = self.patch_api(random_user, [])
        self.assertEqual(response.status_code, 403)

    def patch_api(self, user, data):
        """
        Helper function to make a patch request to the API
        """
        data = json.dumps(data)
        headers = self.build_jwt_headers(user)
        return self.client.patch(self.url, data, **headers, content_type="application/json")

    @mock.patch('edx_exams.apps.router.views.register_exams')
    def test_patch_exams(self, mock_register_exams):
        """
        Request is forwarded to the LMS with exam type
        broken into individual attributes
        """
        data = [
            {
                'course_id': self.course_id,
                'content_id': '123foo',
                'exam_name': 'test practice exam',
                'exam_type': 'practice',
                'backend': 'mockprock'
            },
            {
                'course_id': self.course_id,
                'content_id': '123bar',
                'exam_name': 'test proctored exam',
                'exam_type': 'proctored',
                'backend': 'mockprock'
            },
        ]

        mock_register_exams.return_value = ({}, 200)
        response = self.patch_api(self.user, data)
        self.assertEqual(response.status_code, 200)

        mock_register_exams.assert_called_with(
            self.course_id,
            [
                {
                    'course_id': self.course_id,
                    'content_id': '123foo',
                    'exam_name': 'test practice exam',
                    'exam_type': 'practice',
                    'backend': 'mockprock',
                    'is_proctored': False,
                    'is_practice_exam': True,
                },
                {
                    'course_id': self.course_id,
                    'content_id': '123bar',
                    'exam_name': 'test proctored exam',
                    'exam_type': 'proctored',
                    'backend': 'mockprock',
                    'is_proctored': True,
                    'is_practice_exam': False,
                },
            ]
        )
        self.assertEqual(Exam.objects.all().count(), 1)

    @mock.patch('edx_exams.apps.router.views.register_exams')
    def test_patch_exams_empty(self, mock_register_exams):
        """
        Request is forwarded to the LMS and the api/v1 view is not called
        (no exams in this service should be removed)
        """
        mock_register_exams.return_value = ({}, 200)

        response = self.patch_api(self.user, [])
        self.assertEqual(response.status_code, 200)

        mock_register_exams.assert_called_with(
            self.course_id,
            []
        )
        self.assertEqual(Exam.objects.all().count(), 1)

    @mock.patch('edx_exams.apps.router.views.register_exams')
    def test_patch_exams_missing_type(self, mock_register_exams):
        """
        Requests without an exam type will be forwarded without
        the is_proctored and is_practice_exam fields
        """
        data = [
            {
                'course_id': self.course_id,
                'content_id': '123foo',
                'exam_name': 'test practice exam',
                'backend': 'mockprock'
            }
        ]

        mock_register_exams.return_value = ({}, 200)
        response = self.patch_api(self.user, data)
        self.assertEqual(response.status_code, 200)

        mock_register_exams.assert_called_with(
            self.course_id,
            [
                {
                    'course_id': self.course_id,
                    'content_id': '123foo',
                    'exam_name': 'test practice exam',
                    'backend': 'mockprock',
                }
            ]
        )
        self.assertEqual(Exam.objects.all().count(), 1)

    @mock.patch('edx_exams.apps.router.views.register_exams')
    def test_patch_exams_null_configured_provider(self, mock_register_exams):
        """
        If the configured provider for this course is null this view should
        be called instead of api/v1
        """
        mock_register_exams.return_value = ({}, 200)

        CourseExamConfiguration.objects.create(
            course_id=self.course_id,
            provider=None,
            allow_opt_out=False
        )

        response = self.patch_api(self.user, [])
        self.assertEqual(response.status_code, 200)

        mock_register_exams.assert_called_with(
            self.course_id,
            []
        )
        self.assertEqual(Exam.objects.all().count(), 1)

    @mock.patch('edx_exams.apps.router.views.register_exams')
    def test_patch_exams_failure(self, mock_register_exams):
        """
        And error response from the LMS should be returned with
        the same code
        """
        mock_register_exams.return_value = ("some error", 422)

        response = self.patch_api(self.user, [])
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json(), "some error")


@ddt.ddt
class CourseExamAttemptLegacyViewTest(ExamsAPITestCase):
    """
    Tests for the legacy course exam attempt endpoints
    """

    def setUp(self):
        super().setUp()

        self.course_id = 'course-v1:edx+test+f19'
        self.content_id = 'block-v1:edx+test+f19+type@problem+block@abcd1234'
        self.url = reverse(
            'api:v1:student-course_exam_attempt',
            kwargs={'course_id': self.course_id, 'content_id': self.content_id}
        )

    def get_api(self, user, data):
        """
        Helper function to make a patch request to the API
        """
        data = json.dumps(data)
        headers = self.build_jwt_headers(user)
        return self.client.get(self.url, **headers)

    def test_auth_failures(self):
        """
        Verify the endpoint validates permissions
        """
        # Test unauthenticated
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    @mock.patch('edx_exams.apps.router.views.get_student_exam_attempt_data')
    def test_get_lms_exam_data(self, mock_get_student_exam_attempt_data):
        """
        The exam data should be returned from the LMS
        """
        mock_get_student_exam_attempt_data.return_value = ({
            'exam': {
                "in_timed_exam": True,
                "taking_as_proctored": True,
                "exam_type": "a proctored exam",
                "exam_display_name": "Test Exam",
                "use_legacy_attempt_api": True,
            },
            'active_attempt': {
                "foo": "bar"
            }
        }, 200)

        response = self.get_api(self.user, self.url)
        mock_get_student_exam_attempt_data.assert_called_once_with(
            self.course_id, self.content_id, self.user.lms_user_id
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['exam']['exam_display_name'], 'Test Exam')
        self.assertEqual(response.json().get('active_attempt'), None)
