'''
Tests for the exams LTI views
'''
import uuid
from unittest.mock import patch
from urllib.parse import urljoin

import ddt
from Cryptodome.PublicKey import RSA

from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from lti_consumer.lti_1p3.consumer import LtiConsumer1p3
from lti_consumer.data import Lti1p3LaunchData, Lti1p3ProctoringLaunchData
from lti_consumer.models import LtiConfiguration, LtiProctoringConsumer
from lti_consumer.lti_1p3.consumer import LtiProctoringConsumer
from lti_consumer.lti_1p3.extensions.rest_framework.authentication import Lti1p3ApiAuthentication
from lti_consumer.lti_1p3.extensions.rest_framework.permissions import LtiProctoringAcsPermissions
import json

from edx_exams.apps.api.test_utils import ExamsAPITestCase, UserFactory
from edx_exams.apps.core.models import CourseExamConfiguration, Exam, ExamAttempt
from edx_exams.apps.core.statuses import ExamAttemptStatus
from edx_exams.apps.lti.utils import get_lti_root


@ddt.ddt
class LtiAcsTestCase(ExamsAPITestCase):
    '''
    Test acs view
    '''

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

        # Variables required for testing and verification
        ISS = "http://test-platform.example/"
        OIDC_URL = "http://test-platform/oidc"
        LAUNCH_URL = "http://test-platform/launch"
        REDIRECT_URIS = [LAUNCH_URL]
        CLIENT_ID = "1"
        DEPLOYMENT_ID = "1"
        # NONCE = "1234"
        # STATE = "ABCD"
        RSA_KEY_ID = "1"
        RSA_KEY = RSA.generate(2048).export_key('PEM')

        # Set up consumer
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
            # Set to config on DB for easy testing
            config_store=LtiConfiguration.CONFIG_ON_DB,
            lti_1p3_proctoring_enabled=True,
            # TODO: Fill this object with the other fields/values that match the consumer's IFF we need them,
            # e.g:
            # lti_1p3_oidc_url=OIDC_URL,
        )

        # Update the test provider to refer to the correct LtiConfiguration instance.
        self.test_provider.lti_configuration_id = self.lti_configuration.id
        self.test_provider.save()

        self.url = self.get_acs_url(self.attempt.id)

    def get_acs_url(self, lti_config_id):
        '''
        Return the URL to the acs view.

        Parameters:
            * lti_config_id: the id field of the lti config object
        '''
        return reverse('lti:acs', kwargs={'lti_config_id': lti_config_id})

    def _make_access_token(self, scope):
        '''
        Return a valid token with the required scopes.
        '''
        # Generate a valid access token
        """
        Notes:
        key_handler.encode_and_sign is in the lti 1.3 folder
        """
        print("\n\n#######\nclient_id",self.lti_consumer.client_id)
        print("iss",self.lti_consumer.iss)
        return self.lti_consumer.key_handler.encode_and_sign(
            {
                # 'sub': self.lti_configuration.lti_1p3_client_id,
                'sub': self.lti_consumer.client_id,
                'iss': self.lti_consumer.iss,
                'scopes': scope
            },
            expiration=3600,
        )
        # return {
        #     "access_token": self.lti_consumer.key_handler.encode_and_sign(
        #         {
        #             'sub': self.lti_configuration.lti_1p3_client_id,
        #             'iss': self.lti_consumer.iss,
        #             'scopes': scope
        #         },
        #         expiration=3600,
        #     ),
        #     "token_type": "bearer",
        #     "expires_in": 3600,
        #     "scope": scope
        # }

    # TEST 1: get_attempt successful, status in valid statuses -> Expected log
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
    # @ patch('lti_consumer.lti_1p3.extensions.rest_framework.authentication')
    # @ patch('lti_consumer.lti_1p3.extensions.rest_framework.permissions')
    # @ patch('edx_exams.apps.lti.views.Lti1p3ApiAuthentication.authenticate')
    @ patch.object(Lti1p3ApiAuthentication, 'authenticate', return_value=(AnonymousUser(), None))
    @ patch('edx_exams.apps.lti.views.LtiProctoringAcsPermissions.has_permission')
    @ patch('edx_exams.apps.lti.views.get_user_by_anonymous_id')
    def test_acs_attempt_status(self, attempt_status, expected_response_status, mock_get_attempt, mock_permissions, mock_authentication):
        # print('\n\n\nUSER:', self.user)
        # print('\nUSER ID:', self.user.anonymous_user_id)
        # change attempt status
        self.attempt.status = attempt_status
        # mock of get_user_by_anonymous_id
        mock_get_attempt.return_value = self.attempt
        # print("MOCKS:")
        # print(attempt_status, '\n', expected_response_status, '\n', mock_get_attempt, '\n', mock_permissions, '\n', mock_authentication)

        token = self._make_access_token('https://purl.imsglobal.org/spec/lti-ap/scope/control.all')
        # request body
        request_body = {
            "user": {
                "iss": self.lti_consumer.iss,
                "sub": str(self.user.anonymous_user_id)
            },
            "resource_link": {
                "id": self.exam.resource_id
            },
            "attempt_number": self.attempt.attempt_number,
            "action": "flag",
            "incident_time": "2018-02-01T10:45:33Z",
            "incident_severity": "0.1",
            "reason_code": "12056",
            "reason_msg": "Excessive background noise outside candidate control"
        }
        # Make the request_body with these headers + the data
        # print("\nlti config:", self.lti_configuration)
        # print("\nRequest to URL:", self.url)
        # print("\nTOKEN:", token)
        # print("\nrequest_body:", request_body)
        # print("LTI Config PK id in edx-exams:", self.lti_configuration.id)
        # print("LTI Config in edx-exams:", LtiConfiguration.objects.get(pk=self.lti_configuration.id))

        # mock_authentication.return_value = (AnonymousUser(), None)
        request_body = json.dumps(request_body)
        # print("\n\nREQUEST BODY:",request_body)
        mock_permissions.return_value = True
        response = self.client.post(self.url, data=request_body, content_type="application/json", HTTP_AUTHORIZATION="Bearer {}".format(token))

        expected_msg = (
            f'Flagging exam for user with id {self.user.anonymous_user_id} '
            f'with resource id {self.exam.resource_id} and attempt number {self.attempt.attempt_number} '
            f'for lti config id {self.test_provider.lti_configuration_id}, exam id {self.exam.id}, and attempt id {self.attempt.id}.'
        )

        # assertions
        self.assertEqual(response.status_code, expected_response_status)
        # print("\n\nresponse.data:",response.data)
        # print("\n\nexpected_msg:",expected_msg)
        self.assertEqual(response.data, expected_msg)
        # TODO: Abstract these repeated vars at the start of the function to reduce calls
        print(self.user.anonymous_user_id)
        mock_get_attempt.assert_called_once_with(str(self.user.anonymous_user_id), self.attempt.attempt_number, self.exam.resource_id)

    # TEST 2: get_attempt successful, status NOT in valid statuses -> Expected log
    @ddt.data(

    )
    @ddt.unpack
    def test_acs_attempt_invalid_status(self):
        return

    # TEST 3: get_attempt returned None -> Expected log
    def test_acs_no_attempt_found(self):
        return
        # END


@patch('edx_exams.apps.lti.views.get_lti_1p3_launch_start_url', return_value='https://www.example.com')
class LtiStartProctoringTestCase(ExamsAPITestCase):
    '''
    Test start_proctoring view
    '''

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
        '''
        Return the URL to the start_proctoring view.

        Parameters:
            * attempt_id: the id field of the attempt object
        '''
        return reverse('lti:start_proctoring', kwargs={'attempt_id': attempt_id})

    def test_start_proctoring_launch_data(self, mock_get_lti_launch_url):
        '''
        Test that the instance of Lti1p3LaunchData sent as an argument to get_lti_1p3_launch_start_url
        contains the correct data.
        '''
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
        '''
        Test that calling the start_proctoring view updates the appropriate attempt to the
        'download_software_clicked' status.
        '''
        headers = self.build_jwt_headers(self.user)
        response = self.client.get(self.url, **headers)

        self.attempt.refresh_from_db()

        self.assertRedirects(response, mock_get_lti_launch_url.return_value, fetch_redirect_response=False)
        self.assertEqual(self.attempt.status, ExamAttemptStatus.download_software_clicked)

    def test_start_proctoring_no_attempt(self, mock_get_lti_launch_url):  # pylint: disable=unused-argument
        '''
        Test that a 400 response is returned when calling the start_proctoring view with an attempt_id
        that does not exist.
        '''
        url = self.get_start_proctoring_url(1000)

        headers = self.build_jwt_headers(self.user)
        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, 400)

    def test_start_proctoring_illegal_transition(self, mock_get_lti_launch_url):  # pylint: disable=unused-argument
        '''
        Test that a 403 response is returned when calling the start_proctoring view requests an illegal status
        transition for the attempt_id.
        '''
        self.attempt.status = ExamAttemptStatus.submitted
        self.attempt.save()

        headers = self.build_jwt_headers(self.user)
        response = self.client.get(self.url, **headers)

        self.assertEqual(response.status_code, 403)

    def test_start_proctoring_unauthorized_user(self, mock_get_lti_launch_url):  # pylint: disable=unused-argument
        '''
        Test that a 403 response is returned when calling the start_proctoring view with an attempt_id
        that does not belong to the calling user.
        '''
        other_user = UserFactory()

        headers = self.build_jwt_headers(other_user)
        response = self.client.get(self.url, **headers)

        self.assertEqual(response.status_code, 403)


@patch('edx_exams.apps.lti.views.get_lti_1p3_launch_start_url', return_value='https://www.example.com')
class LtiEndAssessmentTestCase(ExamsAPITestCase):
    '''
    Test end_assessment view
    '''

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
        '''
        Return the URL to the start_proctoring view.

        Parameters:
            * attempt_id: the id field of the attempt object
        '''
        return reverse('lti:end_assessment', kwargs={'attempt_id': attempt_id})

    def test_get_end_assessment_url_launch_data(self, mock_get_lti_launch_url):
        '''
        Test that the instance of Lti1p3LaunchData sent as an argument to get_lti_1p3_launch_start_url
        contains the correct data.
        '''
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
        '''
        Test that calling the end_asessment view updates the appropriate attempt to the
        'submitted' status.
        '''
        headers = self.build_jwt_headers(self.user)
        self.client.get(self.url, **headers)

        self.attempt.refresh_from_db()

        self.assertEqual(self.attempt.status, ExamAttemptStatus.submitted)

    def test_end_assessment_no_attempt(self, mock_get_lti_launch_url):  # pylint: disable=unused-argument
        '''
        Test that a 400 response is returned when calling the end_assessment view with an attempt_id
        that does not exist.
        '''
        url = self.get_end_assessment_url(1000)

        headers = self.build_jwt_headers(self.user)
        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, 400)

    def test_end_assessment_unauthorized_user(self, mock_get_lti_launch_url):  # pylint: disable=unused-argument
        '''
        Test that a 403 response is returned when calling the end_assessment view with an attempt_id
        that does not belong to the calling user.
        '''
        other_user = UserFactory()

        headers = self.build_jwt_headers(other_user)
        response = self.client.get(self.url, **headers)

        self.assertEqual(response.status_code, 403)
