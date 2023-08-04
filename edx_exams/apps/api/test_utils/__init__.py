"""
Test Utilities
"""

from rest_framework.test import APIClient, APITestCase

from edx_exams.apps.api.test_utils.mixins import JwtMixin
from edx_exams.apps.core.models import ProctoringProvider
from edx_exams.apps.core.test_utils.factories import UserFactory

TEST_USERNAME = 'api_worker'
TEST_EMAIL = 'test@email.com'
TEST_PASSWORD = 'QWERTY'


class ExamsAPITestCase(JwtMixin, APITestCase):
    """
    Base class for API Tests
    """

    def setUp(self):
        """
        Perform operations common to all tests.
        """
        super().setUp()
        self.create_user(username=TEST_USERNAME, email=TEST_EMAIL, password=TEST_PASSWORD, is_staff=True)
        self.client = APIClient()
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

        self.test_provider = ProctoringProvider.objects.create(
            name='test_provider',
            verbose_name='testing provider',
            lti_configuration_id='123456789',
            tech_support_phone='1118976309',
            tech_support_email='test@example.com',
        )

    def tearDown(self):
        """
        Perform common tear down operations to all tests.
        """
        # Remove client authentication credentials
        self.client.logout()
        super().tearDown()

    def create_user(self, username=TEST_USERNAME, password=TEST_PASSWORD, is_staff=False, **kwargs):
        """
        Create a test user and set its password.
        """
        self.user = UserFactory(username=username, is_active=True, is_staff=is_staff, **kwargs)
        self.user.set_password(password)
        self.user.save()

    def build_jwt_headers(self, user):
        """
        Set jwt token in cookies.
        """
        jwt_payload = self.default_payload(user)
        jwt_token = self.generate_token(jwt_payload)
        headers = {'HTTP_AUTHORIZATION': 'JWT ' + jwt_token}
        return headers
