"""
LTI Views
"""

from urllib.parse import urljoin

from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from lti_consumer.api import get_end_assessment_return, get_lti_1p3_launch_start_url
from lti_consumer.data import Lti1p3LaunchData, Lti1p3ProctoringLaunchData
from lti_consumer.models import LtiConfiguration
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from edx_exams.apps.core.api import get_attempt_by_id, update_attempt_status
from edx_exams.apps.core.exceptions import ExamIllegalStatusTransition
from edx_exams.apps.core.models import ExamAttempt
from edx_exams.apps.core.statuses import ExamAttemptStatus
from edx_exams.apps.lti.utils import get_lti_root

EDX_OAUTH_BACKEND = 'auth_backends.backends.EdXOAuth2'


@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes((JwtAuthentication,))
@permission_classes((IsAuthenticated,))
def start_proctoring(request, attempt_id):
    """
    LTI Start Proctoring
    """
    # Verify that the attempt associated with attempt_id exists.
    attempt = get_attempt_by_id(attempt_id)
    if not attempt:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={'detail': f'Attempt with attempt_id={attempt_id} does not exit.'}
        )

    # Verify that that the requesting user is authorized to modify the attempt.
    user = request.user
    if attempt.user.id != user.id:
        error_msg = (
            f'user_id={attempt.user.id} attempted to update attempt_id={attempt.id} in '
            f'course_id={attempt.exam.course_id} when starting an LTI launch but does not have access to it.'
        )
        error = {'detail': error_msg}
        return Response(status=status.HTTP_403_FORBIDDEN, data=error)

    try:
        update_attempt_status(attempt_id, ExamAttemptStatus.download_software_clicked)
    except ExamIllegalStatusTransition:
        error_msg = (
            f'user_id={attempt.user.id} attempted to update attempt_id={attempt.id} in '
            f'course_id={attempt.exam.course_id} from status={attempt.status} to '
            f'status={ExamAttemptStatus.download_software_clicked} when starting an LTI launch, but this status '
            f'transition is illegal.'
        )
        error = {'detail': error_msg}
        return Response(status=status.HTTP_403_FORBIDDEN, data=error)

    # user is authenticated via JWT so use that to create a
    # session with this service's authentication backend
    request.user.backend = EDX_OAUTH_BACKEND
    login(request, user)

    exam = attempt.exam
    lti_config_id = exam.provider.lti_configuration_id
    lti_config = LtiConfiguration.objects.get(id=lti_config_id)

    proctoring_start_assessment_url = urljoin(
        get_lti_root(),
        reverse('lti_consumer:lti_consumer.start_proctoring_assessment_endpoint')
    )

    proctoring_launch_data = Lti1p3ProctoringLaunchData(
        attempt_number=attempt.attempt_number,
        start_assessment_url=proctoring_start_assessment_url,
    )

    launch_data = Lti1p3LaunchData(
        user_id=user.id,
        user_role=None,
        config_id=lti_config.config_id,
        resource_link_id=exam.resource_id,
        external_user_id=str(user.anonymous_user_id),
        message_type='LtiStartProctoring',
        proctoring_launch_data=proctoring_launch_data,
    )

    return redirect(get_lti_1p3_launch_start_url(launch_data))


def end_assessment(request, attempt_id):  # pragma: no cover
    """
    LTI End Assessment
    """
    # TODO: Here we'd do all the end of assessment things.
    attempt = ExamAttempt.objects.get(pk=attempt_id)
    exam = attempt.exam
    resource_link_id = exam.resource_id
    end_assessment_return = get_end_assessment_return(request.user.anonymous_user_id, resource_link_id)

    # If end_assessment_return was provided by the Proctoring Tool, and end_assessment was True, then the Assessment
    # Platform MUST send an End Assessment message to the Proctoring Tool. Otherwise, the Assessment Platform can
    # complete its normal post-assessment flow.
    if end_assessment_return:
        lti_config_id = exam.provider.lti_configuration_id
        lti_config = LtiConfiguration.objects.get(id=lti_config_id)

        proctoring_launch_data = Lti1p3ProctoringLaunchData(
            attempt_number=attempt.attempt_number,
        )

        launch_data = Lti1p3LaunchData(
            user_id=request.user.id,
            user_role=None,
            config_id=lti_config.config_id,
            resource_link_id=resource_link_id,
            external_user_id=str(request.user.anonymous_user_id),
            message_type='LtiEndAssessment',
            proctoring_launch_data=proctoring_launch_data,
        )

        # TODO: "If the assessment needs to close due to an error NOT handled by the Assessment Platform that error MUST
        #       be passed along using the LtiEndAssessment message and the errormsg and errorlog claims. The message
        #       utilizes the OpenID connect workflow prior to sending the message." See 4.4 End Assessment Message.
        preflight_url = get_lti_1p3_launch_start_url(launch_data)

        return redirect(preflight_url)

    return JsonResponse({})
