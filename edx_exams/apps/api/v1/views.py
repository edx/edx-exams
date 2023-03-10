"""
V1 API Views
"""
import logging
import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from edx_api_doc_tools import path_parameter, schema
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from token_utils.api import sign_token_for

from edx_exams.apps.api.permissions import StaffUserOrReadOnlyPermissions, StaffUserPermissions
from edx_exams.apps.api.serializers import ExamSerializer, ProctoringProviderSerializer, StudentAttemptSerializer
from edx_exams.apps.api.v1 import ExamsAPIView
from edx_exams.apps.core.api import (
    check_if_exam_timed_out,
    create_exam_attempt,
    get_attempt_by_id,
    get_current_exam_attempt,
    get_exam_attempt_time_remaining,
    get_exam_by_content_id,
    get_latest_attempt_for_user,
    update_attempt_status
)
from edx_exams.apps.core.exam_types import get_exam_type
from edx_exams.apps.core.models import CourseExamConfiguration, Exam, ExamAttempt, ProctoringProvider
from edx_exams.apps.core.statuses import ExamAttemptStatus
from edx_exams.apps.router.interop import get_active_exam_attempt

log = logging.getLogger(__name__)


class CourseExamsView(ExamsAPIView):
    """
    View to modify exams for a specific course.

    Given a list of exam data for a course, this view will either create a new exam (if one doesn't exist), or modify
    an existing exam. Any course exams missing from the request will be marked as inactive.

    HTTP PATCH
    Creates a new Exam.
    Expected PATCH data: [{
        "content_id": 123,
        "exam_name": "Test Examination",
        "time_limit_mins": 30,
        "due_date": "2021-08-04",
        "exam_type": "proctored",
        "hide_after_due": False,
        "is_active": True
    }]
    **PATCH data Parameters**
        * content_id: This will be the pointer to the id of the piece of course_ware which is the proctored exam.
        * exam_name: This is the display name of the Exam (Midterm etc).
        * time_limit_mins: Time limit (in minutes) that a student can finish this exam.
        * due_date: The date on which the exam is due
        * exam_type: Type of exam, i.e. timed, proctored
        * hide_after_due: Whether the exam will be hidden from the learner after the due date has passed.
        * is_active: Whether this exam will be active.
    **Exceptions**
        * HTTP_400_BAD_REQUEST
    """

    authentication_classes = (JwtAuthentication,)
    permission_classes = (StaffUserPermissions,)

    @classmethod
    def update_exam(cls, exam_object, fields):
        """
        Given an exam object, update to the given fields value
        """
        for attr, value in fields.items():
            setattr(exam_object, attr, value)
        exam_object.save()

        log.info(
            "Updated existing exam=%(exam_id)s",
            {
                'exam_id': exam_object.id,
            }
        )

    @classmethod
    def create_exam(cls, fields):
        """
        Create a new exam based on the given fields
        """
        exam = Exam.objects.create(resource_id=str(uuid.uuid4()), **fields)

        log.info(
            "Created new exam=%(exam_id)s",
            {
                'exam_id': exam.id,
            }
        )

    @classmethod
    def handle_exams(cls, request_exams_list, course_exams_qs, course_id):
        """
        Decide how exams should be updated or created
        """
        exams_by_content_id = {}
        for exam in course_exams_qs:
            type_dict = exams_by_content_id.get(exam.content_id)
            if not type_dict:
                exams_by_content_id[exam.content_id] = {}

            exams_by_content_id[exam.content_id][exam.exam_type] = exam

        for exam in request_exams_list:
            # should only be one object per exam type per content_id

            existing_type_exam = exams_by_content_id.get(exam['content_id'], {}).get(exam['exam_type'])

            if existing_type_exam:
                # if the existing exam of the same type is not active,
                # mark all other exams for this content id as inactive
                if not existing_type_exam.is_active:
                    course_exams_qs.filter(content_id=exam['content_id']).update(is_active=False)

                # then update the existing exam
                update_fields = {
                    'exam_name': exam['exam_name'],
                    'time_limit_mins': exam['time_limit_mins'],
                    'due_date': exam['due_date'],
                    'hide_after_due': exam['hide_after_due'],
                    'is_active': exam['is_active'],
                }
                cls.update_exam(existing_type_exam, update_fields)
            else:
                # if existing exam with the type we receive does not exist, mark all other exams inactive
                course_exams_qs.filter(content_id=exam['content_id']).update(is_active=False)

                provider = None
                # get exam type class, which has specific attributes like is_proctored, is_timed, etc.
                exam_type_class = get_exam_type(exam['exam_type'])
                config = CourseExamConfiguration.get_configuration_for_course(course_id)

                # if exam type requires proctoring and the course has a config, use the configured provider
                if exam_type_class and exam_type_class.is_proctored and config:
                    provider = config.provider

                # then create a new exam based on data we received
                exam_fields = {
                    'course_id': course_id,
                    'provider': provider,
                    'content_id': exam['content_id'],
                    'exam_name': exam['exam_name'],
                    'exam_type': exam['exam_type'],
                    'time_limit_mins': exam['time_limit_mins'],
                    'due_date': exam['due_date'],
                    'hide_after_due': exam['hide_after_due'],
                    'is_active': exam['is_active'],
                }
                cls.create_exam(exam_fields)

    @schema(
        body=ExamSerializer(many=True),
        parameters=[
            path_parameter('course_id', str, 'edX course run ID or external course key'),
        ],
        responses={
            200: "OK",
            400: "Invalid request. See message."
        },
        summary='Modify exams',
        description='This endpoint should create new exams, update existing exams, '
                    'and mark any active exams not included in the payload as inactive.'
    )
    def patch(self, request, course_id):
        """
        Create or update a list of exams.
        """
        request_exams = request.data

        serializer = ExamSerializer(data=request_exams, many=True)

        if serializer.is_valid():
            course_exams = Exam.objects.filter(course_id=course_id)

            # decide how to update or create exams based on the request and already existing exams
            self.handle_exams(request_exams, course_exams, course_id)

            # mark any exams not included in the request as inactive. The Query set has already been filtered by course
            remaining_exams = course_exams.exclude(content_id__in=[exam['content_id'] for exam in request_exams])
            remaining_exams.update(is_active=False)

            response_status = status.HTTP_200_OK
            data = {}
        else:
            response_status = status.HTTP_400_BAD_REQUEST
            data = {"detail": "Invalid data", "errors": serializer.errors}

        return Response(status=response_status, data=data)


class CourseExamConfigurationsView(ExamsAPIView):
    """
    View to create and update course exam configs for a specific course.

    Given a course id and a proctoring provider name, this view will either create a new course exam configuration
    (if one doesn't exist), or modify the proctoring provider on an existing course exam config.

    HTTP GET
    Gets CourseExamConfiguration.
    **Returns**
    {
        'provider': 'test_provider',
    }

    HTTP PATCH
    Creates or updates a CourseExamConfiguration.
    Expected PATCH data: {
        'provider': 'test_provider',
    }
    **PATCH data Parameters**
        * name: This is the name of the proctoring provider.
    **Exceptions**
        * HTTP_400_BAD_REQUEST
    """

    authentication_classes = (JwtAuthentication,)
    permission_classes = (StaffUserOrReadOnlyPermissions,)

    def get(self, request, course_id):
        """
        Get exam configuration for a course

        TODO: This view should use a serializer to ensure the read/write bodies are the same
        once more fields are added.
        """
        try:
            provider = CourseExamConfiguration.objects.get(course_id=course_id).provider
        except ObjectDoesNotExist:
            provider = None

        return Response({
            'provider': provider.name if provider else None
        })

    def patch(self, request, course_id):
        """
        Create/update course exam configuration.
        """
        error = None

        # check that proctoring provider is in request
        if 'provider' not in request.data:
            error = {"detail": "No proctoring provider name in request."}
        elif request.data.get('provider') is None:
            provider = None
        else:
            try:
                provider = ProctoringProvider.objects.get(name=request.data['provider'])
            # return 400 if proctoring provider does not exist
            except ObjectDoesNotExist:
                error = {"detail": "Proctoring provider does not exist."}

        if not error:
            CourseExamConfiguration.create_or_update(provider, course_id)
            response_status = status.HTTP_204_NO_CONTENT
            data = {}
        else:
            response_status = status.HTTP_400_BAD_REQUEST
            data = error

        return Response(status=response_status, data=data)


class ProctoringProvidersView(ListAPIView):
    """
    Retrieve a list of all available proctoring providers

    This endpoint returns a list of ProctoringProvider objects

    Path: /api/[version]/providers
    Returns:
     * 200: OK, list of ProctoringProviderObjects
    """

    authentication_classes = (JwtAuthentication,)
    model = ProctoringProvider
    serializer_class = ProctoringProviderSerializer
    queryset = ProctoringProvider.objects.all()


class ExamAccessTokensView(ExamsAPIView):
    """
    View to create signed exam access tokens for a specific user and exam.

    Given an exam_id and user (in request), this view will either grant access
    as an exam access token or not grant access. Access is granted if there is an
    existing exam attempt (must be started if no due date or prior to due date or
    verified if past the due date.) or if the exam is past its due date.

    HTTP GET
    Provides an Exam Access Token as a cookie if access is granted.
    **GET data Parameters**
        * exam_id: This is the id of the exam that the user is requesting access to
    **Exceptions**
        * HTTP_403_FORBIDDEN
    """

    authentication_classes = (JwtAuthentication,)
    permission_classes = (StaffUserOrReadOnlyPermissions,)

    @classmethod
    def get_expiration_window(cls, exam_attempt, default_exp_seconds):
        """
        Set exam access token expiration window.

        Use default exp window or the time to the end of the exam attempt,
        whichever is shorter.
        """
        secs_remaining = get_exam_attempt_time_remaining(exam_attempt)
        # If not past due and attempt time remaining is less than default, set window to remaining
        if 0 <= secs_remaining < default_exp_seconds:
            exp_window = secs_remaining
        else:
            exp_window = default_exp_seconds

        return exp_window

    @classmethod
    def get_response(cls, exam, user):
        """
        Get response, with exam access token if access granted.

        403 error if access is not granted.
        """
        claims = {"course_id": exam.course_id, "content_id": exam.content_id}
        expiration_window = 60
        exam_attempt = ExamAttempt.get_current_exam_attempt(user.id, exam.id)

        data = {"detail": "Exam access token not granted"}
        grant_access = False
        response_status = status.HTTP_403_FORBIDDEN

        # If exam attempt exists for user, then grant exam access
        if exam_attempt is not None:
            # If no due date or if before due date, grant access if attempt started
            # and get expiration window.
            if exam.due_date is None or timezone.now() < exam.due_date:
                if exam_attempt.status == ExamAttemptStatus.started:
                    expiration_window = cls.get_expiration_window(exam_attempt, expiration_window)
                    if expiration_window != 0:
                        grant_access, response_status = True, status.HTTP_200_OK
            # Else (at or after due date),
            # grant access if attempt is submitted or verified
            else:
                if exam_attempt.status in (ExamAttemptStatus.submitted, ExamAttemptStatus.verified) and \
                        not exam.hide_after_due:
                    grant_access, response_status = True, status.HTTP_200_OK

        # If exam is past the due date, then grant exam access
        elif exam.due_date is not None and timezone.now() >= exam.due_date:
            grant_access, response_status = True, status.HTTP_200_OK

        if grant_access:
            log.info("Creating exam access token")
            access_token = sign_token_for(user.lms_user_id, expiration_window, claims)
            data = {"exam_access_token": access_token, "exam_access_token_expiration": expiration_window}

        response = Response(status=response_status,
                            data=data)

        return response

    def get(self, request, exam_id):
        """
        Get exam access token as JWT added as cookie to response.

        Exam access token corresponds to given exam and user in request.
        """
        try:
            exam = Exam.objects.get(id=exam_id)
        except ObjectDoesNotExist:
            response_status = status.HTTP_404_NOT_FOUND
            return Response(status=response_status,
                            data={"detail": "Exam does not exist"})

        response = self.get_response(exam, request.user)

        return response


class LatestExamAttemptView(ExamsAPIView):
    """
    Endpoint for the fetching a user's latest exam attempt.
    /exams/attempt/latest

    Supports:
        HTTP GET: Get the data for a user's latest exam attempt.

    HTTP GET
    Fetches a user's latest exam attempt.
    Status changes to 'submitted' if time remaining is zero.

    **GET data Parameters**
        'user': The data of the user whose latest attempt we want to fetch.

    **Returns**
    {
        'id': int (primary key),
        'created': datetime,
        'modified': datetime,
        'user': User object,
        'start_time': datetime,
        'end_time': datetime,
        'status': string,
        'exam': Exam object,
        'allowed_time_limit_mins': int,
        'attempt_number': int,
    }
    """

    authentication_classes = (JwtAuthentication,)

    def get(self, request):
        """
        HTTP GET handler to fetch all exam attempt data

        Parameters:
            None

        Returns:
            A Response object containing all `ExamAttempt` data.
        """
        user = request.user
        latest_attempt = get_latest_attempt_for_user(user.id)

        if latest_attempt and latest_attempt.status not in (ExamAttemptStatus.started, ExamAttemptStatus.ready_to_submit):
            latest_attempt_legacy = get_active_exam_attempt(user.lms_user_id)
            if latest_attempt_legacy is not None:
                return Response(status=status.HTTP_200_OK, data=latest_attempt_legacy)
    
        if latest_attempt is not None:
            latest_attempt = check_if_exam_timed_out(latest_attempt)

            serialized_attempt = StudentAttemptSerializer(latest_attempt)
            return Response(status=status.HTTP_200_OK, data=serialized_attempt.data)
        
        # no active attempt in either service
        return Response(status=status.HTTP_200_OK, data={})


class ExamAttemptView(ExamsAPIView):
    """
    Endpoint for the ExamAttempt
    /exams/attempt

    Supports:
        HTTP PUT: Update an exam attempt's status.
        HTTP POST: Create an exam attempt.

    HTTP PUT
    Updates the attempt status based on a provided action

    PUT Path Parameters
        'attempt_id': The unique identifier for the exam attempt.

    PUT data Parameters
        'action': The action to perform on the exam attempt. Each action will trigger a status update if appropriate

    PUT Response Values
        {'exam_attempt_id': <attempt_id>}: The attempt id of the attempt being updated

    **Exceptions**
        * HTTP_400_BAD_REQUEST
        * HTTP_403_FORBIDDEN

    HTTP POST
    Creates a new attempt based on a provided exam_id

    POST data Parameters
        'exam_id': The unique identifier for the exam
        'start_clock': Boolean value representing whether or not the attempt should immediately transition to 'started'

    POST Response Values
        {'exam_attempt_id': <attempt_id>}: The attempt id of the attempt that was created
    """

    authentication_classes = (JwtAuthentication,)

    # @staticmethod
    # def course_id_for_request(request, view_args, view_kwargs):
    #     """
    #     Determine if the request should be forwarded to the legacy proctoring service based
    #     on the exam_id provided in the request body.
    #     """
    #     exam_id = request.data.get('exam_id')
    #     if exam_id:
    #         exam = get_exam_by_id(exam_id)
    #         course_id = exam.course_id
        


    def put(self, request, attempt_id):
        """
        HTTP PUT handler to update exam attempt status based on a specified action
        /exams/attempt/<attempt_id>

        Parameters:
            request: The request object
            attempt_id: The unique identifier for the exam attempt.

        Returns:
            A Response object containing the `exam_attempt_id`.
        """

        # get serialized attempt
        attempt = get_attempt_by_id(attempt_id)
        action = request.data.get('action')

        if not attempt:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'detail': f'Attempt with attempt_id={attempt_id} does not exit.'}
            )

        # user should only be able to update their own attempt
        if attempt.user.id != request.user.id:
            error_msg = (
                f"user_id={attempt.user.id} attempted to update attempt_id={attempt.id} in "
                f"course_id={attempt.exam.course_id} but does not have access to it. (action={action})"
            )
            error = {'detail': error_msg}
            return Response(status=status.HTTP_403_FORBIDDEN, data=error)

        action_mapping = {
            'stop': ExamAttemptStatus.ready_to_submit,
            'start': ExamAttemptStatus.started,
            'submit': ExamAttemptStatus.submitted,
            'click_download_software': ExamAttemptStatus.download_software_clicked,
            'error': ExamAttemptStatus.error,
        }

        to_status = action_mapping.get(action)
        if to_status:
            attempt_id = update_attempt_status(attempt_id, to_status)
            data = {"exam_attempt_id": attempt_id}
            return Response(data)

        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={'detail': f'Unrecognized action "{action}"'}
        )

    def post(self, request):
        """
        HTTP POST handler to create exam attempt
        """
        should_start_immediately = request.data.get('start_clock', 'false').lower() == 'true'
        exam_id = request.data.get('exam_id', None)
        user_id = request.user.id

        exam_attempt_id = create_exam_attempt(exam_id, user_id)

        if should_start_immediately:
            update_attempt_status(exam_attempt_id, ExamAttemptStatus.started)

        data = {'exam_attempt_id': exam_attempt_id}
        return Response(data)


class CourseExamAttemptView(ExamsAPIView):
    """
    Endpoint for getting timed or proctored exam and its attempt data given the request user.
    /exam/attempt/course_id/{course_id}/content_id/{content_id}
    Supports:
        HTTP GET:

            Returns an existing exam (by course_id and content id) with a nested attempt object,
            if any attempt for that exam exists.

            Status changes to 'submitted' if time remaining is zero.
            {
                'exam': {
                    'attempt': {...}
                    ...
                },
            }
    """

    def get(self, request, course_id, content_id):
        """
        HTTP GET handler. Returns exam and an attempt, if one exists for the exam
        """
        exam = get_exam_by_content_id(course_id, content_id)

        if exam is None:
            data = {'exam': {}}
            return Response(data)

        serialized_exam = ExamSerializer(exam).data

        exam_type_class = get_exam_type(exam.exam_type)

        # the following are additional fields that the frontend expects
        serialized_exam['type'] = exam.exam_type
        serialized_exam['is_proctored'] = exam_type_class.is_proctored
        serialized_exam['is_practice_exam'] = exam_type_class.is_practice
        serialized_exam['backend'] = exam.provider.verbose_name
        exam_attempt = get_current_exam_attempt(request.user.id, exam.id)
        if exam_attempt is not None:
            exam_attempt = check_if_exam_timed_out(exam_attempt)

            student_attempt = StudentAttemptSerializer(exam_attempt).data
            serialized_exam['attempt'] = student_attempt
        else:
            serialized_exam['attempt'] = {}

        data = {'exam': serialized_exam}
        return Response(data)
