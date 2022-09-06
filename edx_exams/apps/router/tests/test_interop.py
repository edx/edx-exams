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

from edx_exams.apps.router.interop import register_exams


@ddt.ddt
class RegisterExamsTest(TestCase):
    """ Tests for register_exams """

    def setUp(self):
        super().setUp()
        self.course_id = 'course-v1:edx+test+f19'
        self.lms_url = f'{settings.LMS_ROOT_URL}/api/edx_proctoring/v1/proctored_exam/exam_registration/course_id/{self.course_id}'

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
        responder = responses.add(
            responses.PATCH,
            self.lms_url,
            status=response_status,
            json={"foo": "bar"},
        )
        response = register_exams(self.course_id, [])
        self.assertEqual(response.status_code, response_status)
        self.assertEqual(response.json(), {"foo": "bar"})
