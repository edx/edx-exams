"""
LTI Views
"""


import json
import logging
from urllib.parse import urljoin

from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from lti_consumer.api import get_end_assessment_return, get_lti_1p3_launch_start_url
from lti_consumer.data import Lti1p3LaunchData, Lti1p3ProctoringLaunchData
from lti_consumer.lti_1p3.extensions.rest_framework.authentication import Lti1p3ApiAuthentication
from lti_consumer.lti_1p3.extensions.rest_framework.permissions import LtiProctoringAcsPermissions
from lti_consumer.models import LtiConfiguration
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from edx_exams.apps.core.api import (
    get_attempt_for_user_with_attempt_number_and_resource_id,
    get_attempt_by_id,
    update_attempt_status
)
from edx_exams.apps.core.exceptions import ExamIllegalStatusTransition
from edx_exams.apps.core.statuses import ExamAttemptStatus
from edx_exams.apps.lti.utils import get_lti_root
from edx_exams.apps.core.models import User

log = logging.getLogger(__name__)

EDX_OAUTH_BACKEND = 'auth_backends.backends.EdXOAuth2'

LTI_PROCTORING_ASSESSMENT_CONTROL_ACTIONS = [
    'pauseRequest',
    'resumeRequest',
    'terminateRequest',
    'update',
    'flagRequest',
]


@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes((Lti1p3ApiAuthentication,))
@permission_classes((LtiProctoringAcsPermissions,))
def acs(request, lti_config_id):
    """
    Endpoint for ACS actions

    NOTE: for now just have the actions LOG what the actions is doing.
    We can implement proper functionality and tests later once we
    hear back from our third party proctoring service vendors
    (i.e. Verificient and Proctortrack).

    Currently, we only support flagging of exam attempts.
    Other ACS actions (pause, resume, terminate, update) could be implemented
    in the future if desired.
    """
    data = json.loads(request.body)

    # This identifies the proctoring tool the request is coming from.
    user_id = data['user']['sub']
    print("USER ID TYPE:", type(user_id))

    # The link to exam the user is attempting
    resource_id = data['resource_link']['id']

    # Exam attempt number (Note: ACS does not differentiate between launches)
    # i.e, if a launch fails and multiple subsequent launches occur for
    # the same resource_link + attempt_number combo, the ACS only perceives
    # this as one singular attempt.
    attempt_number = data['attempt_number']

    # ACS action to be performed
    action = data['action']

    # Data validation: Make sure that the exam attempt is either ongoing or completed.
    # But not verified, rejected, or expired (no need to flag in these cases)
    # Therefore, any attempt with status from 'started' to 'submitted' can be flagged
    VALID_STATUSES = [
        ExamAttemptStatus.started,
        ExamAttemptStatus.ready_to_submit,
        ExamAttemptStatus.timed_out,
        ExamAttemptStatus.submitted,
    ]

    # TODO: "sub" is actually the "anonymous_user_id"
    # Therefore, we need to get the user's "id" from the "anonymous_user_id"
    # We can do this either within this API function, or via another api.py function.
    attempt = get_attempt_for_user_with_attempt_number_and_resource_id(user_id, attempt_number, resource_id)
    if attempt is None:
        log.info(
            f'No attempt found for user with id {user_id}'
            f'with resource id {resource_id} and attempt number {attempt_number}.'
            f'for lti config id {lti_config_id}.'
        )
    if attempt.status not in VALID_STATUSES:
        log.info(
            f'Attempt cannot be flagged for user with id {user_id}'
            f'with resource id {resource_id} and attempt number {attempt_number}.'
            f'for lti config id {lti_config_id}. It has either not started yet, '
            'been rejcected, expired, or already verified.'
        )
        # NOTE: Do we want to create a new exception in exceptions.py just for this case?
        return Response(status=400)

    if action == 'flag':
        log.info(
            f'Flagging exam for user with id {user_id}'
            f'with resource id {resource_id} and attempt number {attempt_number}.'
            f'for lti config id {lti_config_id}. '
            f'Exam id {attempt.exam.id} '
            f'Attempt id {attempt.id}'
        )

    return Response(action, 200)


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
            data={'detail': f'Attempt with attempt_id={attempt_id} does not exist.'}
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

    assessment_control_url = urljoin(
        get_lti_root(),
        reverse('lti:acs', kwargs={'lti_config_id': lti_config_id}),  # if the url actually existed
    )

    proctoring_launch_data = Lti1p3ProctoringLaunchData(
        attempt_number=attempt.attempt_number,
        start_assessment_url=proctoring_start_assessment_url,
        assessment_control_url=assessment_control_url,
        assessment_control_actions=['flagRequest'],
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


@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes((JwtAuthentication,))
@permission_classes((IsAuthenticated,))
def end_assessment(request, attempt_id):
    """
    LTI End Assessment
    """
    # Verify that the attempt associated with attempt_id exists.
    attempt = get_attempt_by_id(attempt_id)
    if not attempt:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={'detail': f'Attempt with attempt_id={attempt_id} does not exist.'}
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

    update_attempt_status(attempt_id, ExamAttemptStatus.submitted)

    # user is authenticated via JWT so use that to create a
    # session with this service's authentication backend
    request.user.backend = EDX_OAUTH_BACKEND
    login(request, user)

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
