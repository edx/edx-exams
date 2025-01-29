""" Tests for edx-proctoring/LMS interface """
import json
from functools import wraps
from posixpath import join as urljoin

import ddt
import responses
from django.conf import settings
from django.test import TestCase
from requests.exceptions import HTTPError
from rest_framework.exceptions import ValidationError

from edx_exams.apps.router.interop import (
    get_active_exam_attempt,
    get_provider_settings,
    get_student_exam_attempt_data,
    get_user_onboarding_data,
    register_exams
)


@ddt.ddt
class LegacyInteropTest(TestCase):
    """ Tests for edx-proctoring/LMS interface """

    def setUp(self):
        super().setUp()
        self.course_id = 'course-v1:edx+test+f19'
        self.content_id = 'abcd/1234'
        self.lms_user_id = 1
        self.exam_id = 2222

    def mock_oauth_login(fn):
        """
        Mock request to authenticate exams as a backend client
        """
        @wraps(fn)
        def inner(self, *args, **kwargs):
            responses.add(
                responses.POST,
                settings.LMS_ROOT_URL + '/oauth2/access_token',
                body=json.dumps({'access_token': 'abcd', 'expires_in': 60}),
                status=200
            )
            return fn(self, *args, **kwargs)
        return inner

    @ddt.data(200, 422)
    @mock_oauth_login
    @responses.activate
    def test_register_exams(self, response_status):
        """
        Request is authenticated and forwarded to the LMS.
        HTTP exceptions are handled and response is returned for
        non-200 states codes
        """
        self.lms_url = (
            f'{settings.LMS_ROOT_URL}/api/edx_proctoring/v1/proctored_exam/exam_registration/'
            f'course_id/{self.course_id}'
        )
        responder = responses.add(
            responses.PATCH,
            self.lms_url,
            status=response_status,
            json={"foo": "bar"},
        )
        response_data, status = register_exams(self.course_id, [])
        self.assertEqual(status, response_status)
        self.assertEqual(response_data, {"foo": "bar"})

    @ddt.data(200, 422)
    @mock_oauth_login
    @responses.activate
    def test_get_student_attempt_data(self, response_status):
        """
        Request is authenticated and forwarded to the LMS.
        HTTP exceptions are handled and response is returned for
        non-200 states codes
        """
        content_id = 'block-v1:edX+test'
        url_content_id = 'block-v1:edX%2Btest'
        self.lms_url = (
            f'{settings.LMS_ROOT_URL}/api/edx_proctoring/v1/proctored_exam/attempt/course_id/{self.course_id}'
            f'?content_id={url_content_id}&user_id={self.lms_user_id}'
        )
        responder = responses.add(
            responses.GET,
            self.lms_url,
            status=response_status,
            json={"foo": "bar"},
        )
        response_data, status = get_student_exam_attempt_data(self.course_id, content_id, self.lms_user_id)
        self.assertEqual(status, response_status)
        self.assertEqual(response_data, {"foo": "bar"})

    @ddt.data(200, 422)
    @mock_oauth_login
    @responses.activate
    def test_get_active_attempt(self, response_status):
        """
        Request is authenticated and forwarded to the LMS.
        HTTP exceptions are handled and response is returned for
        non-200 states codes
        """
        self.lms_url = (
            f'{settings.LMS_ROOT_URL}/api/edx_proctoring/v1/proctored_exam/active_attempt?user_id={self.lms_user_id}'
        )
        responder = responses.add(
            responses.GET,
            self.lms_url,
            status=response_status,
            json={"foo": "bar"},
        )
        response_data, status = get_active_exam_attempt(self.lms_user_id)
        self.assertEqual(status, response_status)
        self.assertEqual(response_data, {"foo": "bar"})

    @mock_oauth_login
    @responses.activate
    def test_invalid_json_response(self):
        """
        If the LMS returns invalid JSON do not forward this content to the client
        """
        self.lms_url = (
            f'{settings.LMS_ROOT_URL}/api/edx_proctoring/v1/proctored_exam/active_attempt?user_id={self.lms_user_id}'
        )
        responder = responses.add(
            responses.GET,
            self.lms_url,
            status=500,
            body="<invalid json>",
        )
        response_data, status = get_active_exam_attempt(self.lms_user_id)
        self.assertEqual(status, 500)
        self.assertEqual(response_data, {'data': 'Invalid JSON response received from edx-proctoring'})

    @ddt.data(200, 422)
    @mock_oauth_login
    @responses.activate
    def test_get_provider_settings(self, response_status):
        """
        Request is authenticated and forwarded to the LMS.
        HTTP exceptions are handled and response is returned for
        non-200 states codes
        """
        self.lms_url = (
            f'{settings.LMS_ROOT_URL}/api/edx_proctoring/v1/proctored_exam/settings/exam_id/{self.exam_id}/'
        )
        responder = responses.add(
            responses.GET,
            self.lms_url,
            status=response_status,
            json={"foo": "bar"},
        )
        response_data, status = get_provider_settings(self.exam_id)
        self.assertEqual(status, response_status)
        self.assertEqual(response_data, {"foo": "bar"})

    @ddt.data(
        (200, None),
        (422, None),
        (200, 'edx@edx.org'),
        (422, 'edx@edx.org')
    )
    @mock_oauth_login
    @responses.activate
    @ddt.unpack
    def test_get_onboarding_data(self, response_status, username):
        """
        Request is authenticated and forwarded to the LMS.
        HTTP exceptions are handled and response is returned for
        non-200 states codes
        """
        url_course_id = 'course-v1%3Aedx%2Btest%2Bf19'
        url_username = 'edx%40edx.org'

        self.lms_url = (
            f'{settings.LMS_ROOT_URL}/api/edx_proctoring/v1/user_onboarding/status'
            f'?is_learning_mfe=true&course_id={url_course_id}'
        )
        if username:
            self.lms_url += f'&username={url_username}'

        responder = responses.add(
            responses.GET,
            self.lms_url,
            status=response_status,
            json={"foo": "bar"},
        )
        response_data, status = get_user_onboarding_data(self.course_id, username)
        self.assertEqual(status, response_status)
        self.assertEqual(response_data, {"foo": "bar"})
