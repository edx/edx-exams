"""
LTI Views
"""

from urllib.parse import urljoin

from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from lti_consumer.api import get_end_assessment_return, get_lti_1p3_launch_start_url
from lti_consumer.data import Lti1p3LaunchData, Lti1p3ProctoringLaunchData
from lti_consumer.models import LtiConfiguration

from edx_exams.apps.core.models import ExamAttempt
from edx_exams.apps.lti.utils import get_lti_root


@require_http_methods(['GET'])
def start_proctoring(request, attempt_id):
    """
    LTI Start Proctoring
    """
    # TODO: Here we'd do all the start of proctoring things.

    exam_attempt = ExamAttempt.objects.get(pk=attempt_id)
    exam = exam_attempt.exam
    lti_config_id = exam.provider.lti_configuration_id
    lti_config = LtiConfiguration.objects.get(id=lti_config_id)

    proctoring_start_assessment_url = urljoin(
        get_lti_root(),
        reverse('lti_consumer:lti_consumer.start_proctoring_assessment_endpoint')
    )

    proctoring_launch_data = Lti1p3ProctoringLaunchData(
        attempt_number=exam_attempt.attempt_number,
        start_assessment_url=proctoring_start_assessment_url,
    )

    launch_data = Lti1p3LaunchData(
        user_id=request.user.id,
        user_role=None,
        config_id=lti_config.config_id,
        resource_link_id=exam.resource_id,
        external_user_id=str(request.user.anonymous_user_id),
        message_type="LtiStartProctoring",
        proctoring_launch_data=proctoring_launch_data,
    )

    return redirect(get_lti_1p3_launch_start_url(launch_data))


def end_assessment(request, attempt_id):
    """
    LTI End Assessment
    """
    # TODO: Here we'd do all the end of assessment things.
    exam_attempt = ExamAttempt.objects.get(pk=attempt_id)
    exam = exam_attempt.exam
    resource_link_id = exam.resource_id
    end_assessment_return = get_end_assessment_return(request.user.anonymous_user_id, resource_link_id)

    # If end_assessment_return was provided by the Proctoring Tool, and end_assessment was True, then the Assessment
    # Platform MUST send an End Assessment message to the Proctoring Tool. Otherwise, the Assessment Platform can
    # complete its normal post-assessment flow.
    if end_assessment_return:
        lti_config_id = exam.provider.lti_configuration_id
        lti_config = LtiConfiguration.objects.get(id=lti_config_id)

        proctoring_launch_data = Lti1p3ProctoringLaunchData(
            attempt_number=exam_attempt.attempt_number,
        )

        launch_data = Lti1p3LaunchData(
            user_id=request.user.id,
            user_role=None,
            config_id=lti_config.config_id,
            resource_link_id=resource_link_id,
            external_user_id=str(request.user.anonymous_user_id),
            message_type="LtiEndAssessment",
            proctoring_launch_data=proctoring_launch_data,
        )

        # TODO: "If the assessment needs to close due to an error NOT handled by the Assessment Platform that error MUST
        #       be passed along using the LtiEndAssessment message and the errormsg and errorlog claims. The message
        #       utilizes the OpenID connect workflow prior to sending the message." See 4.4 End Assessment Message.
        preflight_url = get_lti_1p3_launch_start_url(launch_data)

        return redirect(preflight_url)

    return JsonResponse({})
