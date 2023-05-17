"""
Tests for the exams LTI views
"""
import logging
import json
import uuid
from unittest.mock import patch
from urllib.parse import urljoin

import ddt
from Cryptodome.PublicKey import RSA
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from lti_consumer.data import Lti1p3LaunchData, Lti1p3ProctoringLaunchData
from lti_consumer.lti_1p3.extensions.rest_framework.authentication import Lti1p3ApiAuthentication
from lti_consumer.models import LtiConfiguration, LtiProctoringConsumer

from edx_exams.apps.api.test_utils import ExamsAPITestCase, UserFactory
from edx_exams.apps.api.test_utils.factories import CourseExamConfigurationFactory, ExamFactory, ExamAttemptFactory
from edx_exams.apps.core.models import CourseExamConfiguration, Exam, ExamAttempt
from edx_exams.apps.core.statuses import ExamAttemptStatus
from edx_exams.apps.lti.utils import get_lti_root

log = logging.getLogger(__name__)


@ddt.ddt
class LtiAcsTestCase(ExamsAPITestCase):
    """
    Test acs view
    """

    def setUp(self):
        super().setUp()

        self.course_exam_config = CourseExamConfigurationFactory()
        self.exam = ExamFactory()
        self.attempt = ExamAttemptFactory()

        # Variables required for testing and verification
        ISS = 'http://test-platform.example/'
        OIDC_URL = 'http://test-platform/oidc'
        LAUNCH_URL = 'http://test-platform/launch'
        REDIRECT_URIS = [LAUNCH_URL]
        CLIENT_ID = '1'
        DEPLOYMENT_ID = '1'
        RSA_KEY_ID = '1'
        RSA_KEY = RSA.generate(2048).export_key('PEM')

        # Set up consumer
        self.lti_consumer = LtiProctoringConsumer(
            iss=ISS,
            lti_oidc_url=OIDC_URL,
            lti_launch_url=LAUNCH_URL,
            client_id=CLIENT_ID,
            deployment_id=DEPLOYMENT_ID,
            rsa_key=RSA_KEY,
            rsa_key_id=RSA_KEY_ID,
            redirect_uris=REDIRECT_URIS,
            # Use the same key for testing purposes
            tool_key=RSA_KEY
        )

        # Create an LtiConfiguration instance so that the config's client_id can be included in the Lti1p3LaunchData.
        self.lti_configuration = LtiConfiguration.objects.create(
            version=LtiConfiguration.LTI_1P3,
            lti_1p3_client_id=CLIENT_ID,
            config_store=LtiConfiguration.CONFIG_ON_DB,  # Set to config on DB for easy testing
            lti_1p3_proctoring_enabled=True,
        )

        # Update the test provider to refer to the correct LtiConfiguration instance.
        self.test_provider.lti_configuration_id = self.lti_configuration.id
        self.test_provider.save()

        self.url = self.get_acs_url(self.attempt.id)

    def get_acs_url(self, lti_config_id):
        """
        Return the URL to the acs view.

        Parameters:
            * lti_config_id: the id field of the lti config object
        """
        return reverse('lti:acs', kwargs={'lti_config_id': lti_config_id})

    def make_access_token(self, scope):
        """
        Return a valid token with the required scopes.

        Notes:
        key_handler.encode_and_sign is in the lti 1.3 folder
        """
        return self.lti_consumer.key_handler.encode_and_sign(
            {
                'sub': self.lti_consumer.client_id,
                'iss': self.lti_consumer.iss,
                'scopes': scope
            },
            expiration=3600,
        )

    def create_request_body(self, attempt_number):
        """
        Return a template for the data sent in the request to the ACS endpoint.
        """
        return {
            'user': {
                'iss': self.lti_consumer.iss,
                'sub': str(self.user.anonymous_user_id)
            },
            'resource_link': {
                'id': self.exam.resource_id
            },
            'attempt_number': attempt_number,
            'action': 'flag',
            'incident_time': '2018-02-01T10:45:33Z',
            'incident_severity': '0.1',
            'reason_code': '12056',
            'reason_msg': 'Excessive background noise outside candidate control'
        }

    @ ddt.data(
        (ExamAttemptStatus.ready_to_start, 200),
        (ExamAttemptStatus.started, 200),
        (ExamAttemptStatus.ready_to_submit, 200),
        (ExamAttemptStatus.timed_out, 200),
        (ExamAttemptStatus.submitted, 200),
        (ExamAttemptStatus.created, 400),
        (ExamAttemptStatus.download_software_clicked, 400),
        (ExamAttemptStatus.verified, 400),
        (ExamAttemptStatus.rejected, 400),
        (ExamAttemptStatus.expired, 400),
    )
    @ ddt.unpack
    @ patch.object(Lti1p3ApiAuthentication, 'authenticate', return_value=(AnonymousUser(), None))
    @ patch('edx_exams.apps.lti.views.LtiProctoringAcsPermissions.has_permission')
    @ patch('edx_exams.apps.lti.views.get_attempt_for_user_with_attempt_number_and_resource_id')
    def test_acs_attempt_status(self,
                                attempt_status,
                                expected_response_status,
                                mock_get_attempt,
                                mock_permissions,
                                mock_authentication):  # pylint: disable=unused-argument
        """
        Test that certain exam attempt statuses return the expected response code
        """
        self.attempt.status = attempt_status

        mock_get_attempt.return_value = self.attempt
        mock_permissions.return_value = True

        token = self.make_access_token('https://purl.imsglobal.org/spec/lti-ap/scope/control.all')

        request_body = self.create_request_body(self.attempt.attempt_number)

        # Even though the client.post function below uses json.dumps to serialize the request as json,
        # The json serialization needs to happen before the request for an unknown reason
        request_body = json.dumps(request_body)
        response = self.client.post(self.url, data=request_body, content_type='application/json',
                                    HTTP_AUTHORIZATION='Bearer {}'.format(token))

        self.assertEqual(response.status_code, expected_response_status)

    @ patch.object(Lti1p3ApiAuthentication, 'authenticate', return_value=(AnonymousUser(), None))
    @ patch('edx_exams.apps.lti.views.LtiProctoringAcsPermissions.has_permission')
    @ patch('edx_exams.apps.lti.views.get_attempt_for_user_with_attempt_number_and_resource_id')
    def test_acs_no_attempt_found(self,
                                  mock_get_attempt,
                                  mock_permissions,
                                  mock_authentication):  # pylint: disable=unused-argument
        """
        Test that if an exam attempt is not found that the view returns status=400
        """
        false_attempt_number = '88888888'

        mock_get_attempt.return_value = None
        mock_permissions.return_value = True

        token = self.make_access_token('https://purl.imsglobal.org/spec/lti-ap/scope/control.all')

        # Request w/ attempt number for an attempt that does not exist
        request_body = self.create_request_body(false_attempt_number)

        # Even though the client.post function below uses json.dumps to serialize the request as json,
        # The json serialization needs to happen before the request for an unkown reason
        request_body = json.dumps(request_body)
        response = self.client.post(self.url, data=request_body, content_type='application/json',
                                    HTTP_AUTHORIZATION='Bearer {}'.format(token))

        self.assertEqual(response.status_code, 400)

    def test_auth_failures(self):
        """
        Test that an exception occurs if basic access token authentication fails
        """
        token = "invalid_token"
        response = self.client.post(self.url, HTTP_AUTHORIZATION='Bearer {}'.format(token))
        self.assertEqual(response.status_code, 403)

    @ patch.object(Lti1p3ApiAuthentication, 'authenticate', return_value=(AnonymousUser(), None))
    def test_permission_failures(self, mock_authentication):  # pylint: disable=unused-argument
        """
        Test that an exception occurs if the ACS scope is not present in the request's access token
        """
        token = self.make_access_token("invalid_scope")
        print('Bearer {}'.format(token))
        request_body = self.create_request_body(self.attempt.attempt_number)
        response = self.client.post(self.url, data=request_body, content_type='application/json',
                                    HTTP_AUTHORIZATION='Bearer {}'.format(token))
        self.assertEqual(response.status_code, 403)


@patch('edx_exams.apps.lti.views.get_lti_1p3_launch_start_url', return_value='https://www.example.com')
class LtiStartProctoringTestCase(ExamsAPITestCase):
    """
    Test start_proctoring view
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

        self.attempt = ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1111111,
            status=ExamAttemptStatus.created,
            start_time=None,
            allowed_time_limit_mins=None,
        )

        # Create an LtiConfiguration instance so that the config_id can be included in the Lti1p3LaunchData.
        self.lti_configuration = LtiConfiguration.objects.create()

        # Update the test provider to refer to the correct LtiConfiguration instance.
        self.test_provider.lti_configuration_id = self.lti_configuration.id
        self.test_provider.save()

        self.url = self.get_start_proctoring_url(self.attempt.id)

    def get_start_proctoring_url(self, attempt_id):
        """
        Return the URL to the start_proctoring view.

        Parameters:
            * attempt_id: the id field of the attempt object
        """
        return reverse('lti:start_proctoring', kwargs={'attempt_id': attempt_id})

    def test_start_proctoring_launch_data(self, mock_get_lti_launch_url):
        """
        Test that the instance of Lti1p3LaunchData sent as an argument to get_lti_1p3_launch_start_url
        contains the correct data.
        """
        headers = self.build_jwt_headers(self.user)
        self.client.get(self.url, **headers)

        expected_proctoring_start_assessment_url = urljoin(
            get_lti_root(),
            reverse('lti_consumer:lti_consumer.start_proctoring_assessment_endpoint')
        )
        expected_proctoring_launch_data = Lti1p3ProctoringLaunchData(
            attempt_number=self.attempt.attempt_number,
            start_assessment_url=expected_proctoring_start_assessment_url,
            assessment_control_url='http://test.exams:18740/lti/1/acs',
            assessment_control_actions=['flagRequest'],
        )

        expected_launch_data = Lti1p3LaunchData(
            user_id=self.user.id,
            user_role=None,
            config_id=self.lti_configuration.config_id,
            resource_link_id=self.exam.resource_id,
            external_user_id=str(self.user.anonymous_user_id),
            message_type='LtiStartProctoring',
            proctoring_launch_data=expected_proctoring_launch_data
        )

        mock_get_lti_launch_url.assert_called_with(expected_launch_data)

    def test_start_proctoring_updated_attempt(self, mock_get_lti_launch_url):
        """
        Test that calling the start_proctoring view updates the appropriate attempt to the
        'download_software_clicked' status.
        """
        headers = self.build_jwt_headers(self.user)
        response = self.client.get(self.url, **headers)

        self.attempt.refresh_from_db()

        self.assertRedirects(response, mock_get_lti_launch_url.return_value, fetch_redirect_response=False)
        self.assertEqual(self.attempt.status, ExamAttemptStatus.download_software_clicked)

    def test_start_proctoring_no_attempt(self, mock_get_lti_launch_url):  # pylint: disable=unused-argument
        """
        Test that a 400 response is returned when calling the start_proctoring view with an attempt_id
        that does not exist.
        """
        url = self.get_start_proctoring_url(1000)

        headers = self.build_jwt_headers(self.user)
        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, 400)

    def test_start_proctoring_illegal_transition(self, mock_get_lti_launch_url):  # pylint: disable=unused-argument
        """
        Test that a 403 response is returned when calling the start_proctoring view requests an illegal status
        transition for the attempt_id.
        """
        self.attempt.status = ExamAttemptStatus.submitted
        self.attempt.save()

        headers = self.build_jwt_headers(self.user)
        response = self.client.get(self.url, **headers)

        self.assertEqual(response.status_code, 403)

    def test_start_proctoring_unauthorized_user(self, mock_get_lti_launch_url):  # pylint: disable=unused-argument
        """
        Test that a 403 response is returned when calling the start_proctoring view with an attempt_id
        that does not belong to the calling user.
        """
        other_user = UserFactory()

        headers = self.build_jwt_headers(other_user)
        response = self.client.get(self.url, **headers)

        self.assertEqual(response.status_code, 403)


@patch('edx_exams.apps.lti.views.get_lti_1p3_launch_start_url', return_value='https://www.example.com')
class LtiEndAssessmentTestCase(ExamsAPITestCase):
    """
    Test end_assessment view
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

        self.attempt = ExamAttempt.objects.create(
            user=self.user,
            exam=self.exam,
            attempt_number=1111111,
            status=ExamAttemptStatus.created,
            start_time=None,
            allowed_time_limit_mins=None,
        )

        # Create an LtiConfiguration instance so that the config_id can be included in the Lti1p3LaunchData.
        self.lti_configuration = LtiConfiguration.objects.create()

        # Update the test provider to refer to the correct LtiConfiguration instance.
        self.test_provider.lti_configuration_id = self.lti_configuration.id
        self.test_provider.save()

        self.url = self.get_end_assessment_url(self.attempt.id)

    def get_end_assessment_url(self, attempt_id):
        """
        Return the URL to the start_proctoring view.

        Parameters:
            * attempt_id: the id field of the attempt object
        """
        return reverse('lti:end_assessment', kwargs={'attempt_id': attempt_id})

    def test_get_end_assessment_url_launch_data(self, mock_get_lti_launch_url):
        """
        Test that the instance of Lti1p3LaunchData sent as an argument to get_lti_1p3_launch_start_url
        contains the correct data.
        """
        with patch('edx_exams.apps.lti.views.get_end_assessment_return', return_value=True):
            headers = self.build_jwt_headers(self.user)
            self.client.get(self.url, **headers)

        expected_proctoring_launch_data = Lti1p3ProctoringLaunchData(
            attempt_number=self.attempt.attempt_number,
        )

        expected_launch_data = Lti1p3LaunchData(
            user_id=self.user.id,
            user_role=None,
            config_id=self.lti_configuration.config_id,
            resource_link_id=self.exam.resource_id,
            external_user_id=str(self.user.anonymous_user_id),
            message_type='LtiEndAssessment',
            proctoring_launch_data=expected_proctoring_launch_data
        )

        mock_get_lti_launch_url.assert_called_with(expected_launch_data)

    def test_end_assessment_redirect(self, mock_get_lti_launch_url):
        with patch('edx_exams.apps.lti.views.get_end_assessment_return', return_value=True):
            headers = self.build_jwt_headers(self.user)
            response = self.client.get(self.url, **headers)

        self.assertRedirects(response, mock_get_lti_launch_url.return_value, fetch_redirect_response=False)

    def test_end_assessment_no_redirect(self, mock_get_lti_launch_url):  # pylint: disable=unused-argument
        with patch('edx_exams.apps.lti.views.get_end_assessment_return', return_value=False):
            headers = self.build_jwt_headers(self.user)
            response = self.client.get(self.url, **headers)

        self.assertEqual(response.status_code, 200)

    def test_end_assessment_updated_attempt(self, mock_get_lti_launch_url):  # pylint: disable=unused-argument
        """
        Test that calling the end_asessment view updates the appropriate attempt to the
        'submitted' status.
        """
        headers = self.build_jwt_headers(self.user)
        self.client.get(self.url, **headers)

        self.attempt.refresh_from_db()

        self.assertEqual(self.attempt.status, ExamAttemptStatus.submitted)

    def test_end_assessment_no_attempt(self, mock_get_lti_launch_url):  # pylint: disable=unused-argument
        """
        Test that a 400 response is returned when calling the end_assessment view with an attempt_id
        that does not exist.
        """
        url = self.get_end_assessment_url(1000)

        headers = self.build_jwt_headers(self.user)
        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, 400)

    def test_end_assessment_unauthorized_user(self, mock_get_lti_launch_url):  # pylint: disable=unused-argument
        """
        Test that a 403 response is returned when calling the end_assessment view with an attempt_id
        that does not belong to the calling user.
        """
        other_user = UserFactory()

        headers = self.build_jwt_headers(other_user)
        response = self.client.get(self.url, **headers)

        self.assertEqual(response.status_code, 403)
