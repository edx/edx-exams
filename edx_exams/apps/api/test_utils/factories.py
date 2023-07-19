"""
Factories for exams tests
"""

import datetime

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from edx_exams.apps.core.models import (
    AssessmentControlResult,
    CourseExamConfiguration,
    Exam,
    ExamAttempt,
    ProctoringProvider
)
from edx_exams.apps.core.statuses import ExamAttemptStatus


class UserFactory(DjangoModelFactory):
    """
    Factory to create users to be used in other unit tests
    """

    class Meta:
        model = get_user_model()
        django_get_or_create = (
            'email',
            'username',
        )

    _DEFAULT_PASSWORD = 'test'

    username = factory.Sequence('user{}'.format)
    email = factory.Sequence('user+test+{}@edx.org'.format)
    password = factory.PostGenerationMethodCall('set_password', _DEFAULT_PASSWORD)
    first_name = factory.Sequence('User{}'.format)
    last_name = 'Test'
    is_superuser = False
    is_staff = False


class ProctoringProviderFactory(DjangoModelFactory):
    """
    Factory to create proctoring providers to be used in other unit tests
    """
    class Meta:
        model = ProctoringProvider

    name = factory.Sequence('test_provider_{}'.format)
    verbose_name = factory.Sequence('Test Provider {}'.format)
    lti_configuration_id = factory.Sequence('11{}'.format)
    tech_support_phone = '1118976309'
    tech_support_email = 'test@example.com'


class CourseExamConfigurationFactory(DjangoModelFactory):
    """
    Factory to create course exam configurations to be used in other unit tests
    """
    class Meta:
        model = CourseExamConfiguration

    course_id = 'course-v1:edX+Test+Test_Course'
    provider = factory.SubFactory(ProctoringProviderFactory)
    allow_opt_out = False


class ExamFactory(DjangoModelFactory):
    """
    Factory to create exams to be used in other unit tests
    """
    class Meta:
        model = Exam

    resource_id = str(factory.Sequence('resource{}'.format))
    course_id = 'course-v1:edX+Test+Test_Course'
    content_id = factory.Sequence('block-v1:edX+test+2023+type@sequential+block@1111111111{}'.format)
    provider = factory.SubFactory(ProctoringProviderFactory)
    exam_name = factory.Sequence('exam{}'.format)
    exam_type = 'proctored'
    time_limit_mins = 30
    due_date = datetime.datetime.now() + datetime.timedelta(days=1)


class ExamAttemptFactory(DjangoModelFactory):
    """
    Factory to create exam attempts to be used in other unit tests
    """
    class Meta:
        model = ExamAttempt

    exam = factory.SubFactory(ExamFactory)
    user = factory.SubFactory(UserFactory)
    attempt_number = 1
    status = ExamAttemptStatus.created
    start_time = None
    allowed_time_limit_mins = 30


class AssessmentControlResultFactory(DjangoModelFactory):
    """
    Factory to create assessment control results
    """
    class Meta:
        model = AssessmentControlResult

    attempt = factory.SubFactory(ExamAttemptFactory)
    action_type = 'terminate'
    incident_time = datetime.datetime.now() - datetime.timedelta(hours=1)
    severity = 1
    reason_code = '1'
