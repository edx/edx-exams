"""
LTI Views
"""


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
    get_attempt_by_id,
    get_attempt_for_user_with_attempt_number_and_resource_id,
    get_exam_by_id,
    update_attempt_status
)
from edx_exams.apps.core.exceptions import ExamIllegalStatusTransition
from edx_exams.apps.core.models import User
from edx_exams.apps.core.statuses import ExamAttemptStatus
from edx_exams.apps.lti.utils import get_lti_root

log = logging.getLogger(__name__)

EDX_OAUTH_BACKEND = 'auth_backends.backends.EdXOAuth2'


@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes((Lti1p3ApiAuthentication,))
@permission_classes((LtiProctoringAcsPermissions,))
def acs(request, lti_config_id):
    """
    Endpoint for ACS actions

    NOTE: for now just have the actions LOG what the actions is doing.
    We can implement proper functionality and tests later once we
    hear back from our third party proctoring service vendors (i.e. Proctorio).

    Currently, we only support flagging of exam attempts.
    Other ACS actions (pause, resume, terminate, update) could be implemented
    in the future if desired.
    """
    data = request.data

    # This identifies the proctoring tool the request is coming from.
    anonymous_user_id = data['user']['sub']

    # The link to exam the user is attempting
    resource_id = data['resource_link']['id']

    # Exam attempt number (Note: ACS does not differentiate between launches)
    # i.e, if a launch fails and multiple subsequent launches occur for
    # the same resource_link + attempt_number combo, the ACS only perceives
    # this as one singular attempt.
    attempt_number = data['attempt_number']

    # ACS action to be performed
    action = data['action']

    # Only flag ongoing or completed attempts
    VALID_STATUSES = [
        ExamAttemptStatus.ready_to_start,
        ExamAttemptStatus.started,
        ExamAttemptStatus.ready_to_submit,
        ExamAttemptStatus.timed_out,
        ExamAttemptStatus.submitted,
    ]

    user_id = User.objects.get(anonymous_user_id=anonymous_user_id).id
    attempt = get_attempt_for_user_with_attempt_number_and_resource_id(user_id, attempt_number, resource_id)
    from pprint import pprint
    print("\n\nself.attempt got in view")
    pprint(vars(attempt))
    if attempt is None:
        error_msg = (
            f'No attempt found for user with anonymous id {anonymous_user_id} '
            f'with resource id {resource_id} and attempt number {attempt_number} '
            f'for lti config id {lti_config_id}.'
        )
        log.info(error_msg)
        return Response(status=400)
    if attempt.status not in VALID_STATUSES:
        error_msg = (
            f'Attempt cannot be flagged for user with anonymous id {anonymous_user_id} '
            f'with resource id {resource_id} and attempt number {attempt_number} '
            f'for lti config id {lti_config_id}, status {attempt.status}, exam id {attempt.exam.id}, '
            f'and attempt id {attempt.id}. It has either not started yet, been rejected, expired, or already verified.'
        )
        log.info(error_msg)
        return Response(status=400)

    if action == 'flag':
        # TODO: Make the flag action actually modify the exam attempt data (or perhaps another model?)
        success_msg = (
            f'Flagging exam attempt for user with id {anonymous_user_id} '
            f'with resource id {resource_id} and attempt number {attempt_number} '
            f'for lti config id {lti_config_id}, status {attempt.status}, exam id {attempt.exam.id}, '
            f'and attempt id {attempt.id}.'
        )
        log.info(success_msg)

    # Yeah we should probably store them somewhere... 
    # In a perfect world that would be configurable by provider outside the codebase 
    # along with what codes are error and what codes are success. 
    # Sounds like a followup for when we add a second provider to me. 
    # Maybe we just add some constants or something to map this right now?

    # Leaning toward a simple solution right now which could be:

    # "1" is a success and anything else is an error
    # We keep a map of display labels on the backend for error codes and return that display label instead of the code in the serializer.

    # Other codes: Zach added these in his PR so we will just merge with that
    # 0 : Disconnected from Proctorio
    # 1 : Submitted
    # 2 : Navigated away from the exam
    # 4 : Left exam when in full screen
    # 5 : Ended screen recording
    # 6 : Uninstalled Chrome Extension
    # 7 : Switched to a proxy during the exam
    # 8 : Changed networks during the exam
    # 9 : Closed or reloaded the exam tab
    # 12 : Attempted to modify the quiz page
    # 13 : Attempted to download a file during the quiz
    # 14 : The battery died
    # 15 : Plugged in an additional monitor
    # 16 : Unplugged a camera or microphone
    # 21 : Page became unresponsive during the exam
    # 24 : Revoked the microphone permission
    # 25 : Revoked the webcam permission

    elif action == 'terminate':
        # Upon receiving a terminate request, the attempt referenced in the request should be moved to a corresponding status,
        # depending on the reason for termination (reason_code) and incident_severity.

        # Get the reason code for the termination
        reason_code = data['reason_code']
        # Get the severity
        severity = float(data['incident_severity'])
        SEVERITY_THRESHOLD = 0.25
        success_msg = ''

        # Reason codes:
        if reason_code == 'user_submission':
            # terminate with severity > 0.25 will move to second_review_required otherwise verified
            if severity > SEVERITY_THRESHOLD:
                update_attempt_status(attempt.id, 'second_review_required')
                print("\n\That same attempt after update")
                pprint(vars(attempt))
                success_msg = (
                    f'Termination Severity > 0.25, marking exam attempt for secondary review. '
                    f'Terminating exam attempt for user with id {anonymous_user_id} '
                    f'with resource id {resource_id} and attempt number {attempt_number} '
                    f'for lti config id {lti_config_id}, status {attempt.status}, exam id {attempt.exam.id}, '
                    f'and attempt id {attempt.id}.'
                )
            elif severity <= SEVERITY_THRESHOLD:
                update_attempt_status(attempt.id, 'verified')
                success_msg = (
                    f'Termination Severity <= 0.25, marking exam attempt as verified. '
                    f'Terminating exam attempt for user with id {anonymous_user_id} '
                    f'with resource id {resource_id} and attempt number {attempt_number} '
                    f'for lti config id {lti_config_id}, status {attempt.status}, exam id {attempt.exam.id}, '
                    f'and attempt id {attempt.id}.'
                )
                log.info(success_msg)
        elif reason_code == 'error':
            # error: set attempt status to error
            print('error')

    return Response(success_msg, status=200)


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
        reverse('lti:acs', kwargs={'lti_config_id': lti_config_id}),
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
        context_id=exam.course_id,
        context_label=exam.content_id,
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
            context_id=exam.course_id,
        )

        # TODO: "If the assessment needs to close due to an error NOT handled by the Assessment Platform that error MUST
        #       be passed along using the LtiEndAssessment message and the errormsg and errorlog claims. The message
        #       utilizes the OpenID connect workflow prior to sending the message." See 4.4 End Assessment Message.
        preflight_url = get_lti_1p3_launch_start_url(launch_data)

        return redirect(preflight_url)

    return JsonResponse({})


@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes((JwtAuthentication,))
@permission_classes((IsAuthenticated,))
def launch_instructor_tool(request, exam_id):
    """
    View to initiate an LTI launch of the Instructor Tool for an exam.
    """
    user = request.user

    # TODO: this should eventually be replaced with a permission check
    # for course staff
    if not user.is_staff:
        return Response(status=status.HTTP_403_FORBIDDEN)

    exam = get_exam_by_id(exam_id)
    if not exam:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={'detail': f'Exam with exam_id={exam_id} does not exist.'}
        )

    lti_config_id = exam.provider.lti_configuration_id
    lti_config = LtiConfiguration.objects.get(id=lti_config_id)
    launch_data = Lti1p3LaunchData(
        user_id=user.id,
        user_role='instructor',
        config_id=lti_config.config_id,
        resource_link_id=exam.resource_id,
        external_user_id=str(user.anonymous_user_id),
        context_id=exam.course_id,
    )

    return redirect(get_lti_1p3_launch_start_url(launch_data))
