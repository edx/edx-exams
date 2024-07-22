"""
V1 API Views
"""
import logging
import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone
from edx_api_doc_tools import path_parameter, schema
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from token_utils.api import sign_token_for

from edx_exams.apps.api.permissions import CourseStaffOrReadOnlyPermissions, CourseStaffUserPermissions
from edx_exams.apps.api.serializers import (
    AllowanceSerializer,
    CourseExamConfigurationReadSerializer,
    CourseExamConfigurationWriteSerializer,
    ExamSerializer,
    InstructorViewAttemptSerializer,
    ProctoringProviderSerializer,
    StudentAttemptSerializer
)
from edx_exams.apps.api.v1 import ExamsAPIView
from edx_exams.apps.core.api import (
    check_if_exam_timed_out,
    create_exam_attempt,
    create_or_update_course_exam_configuration,
    get_active_attempt_for_user,
    get_attempt_by_id,
    get_course_exam_configuration_by_course_id,
    get_course_exams,
    get_current_exam_attempt,
    get_exam_attempt_time_remaining,
    get_exam_attempts,
    get_exam_by_content_id,
    get_exam_by_id,
    get_provider_by_exam_id,
    is_exam_passed_due,
    reset_exam_attempt,
    update_attempt_status
)
from edx_exams.apps.core.exam_types import get_exam_type
from edx_exams.apps.core.models import (
    CourseExamConfiguration,
    Exam,
    ExamAttempt,
    ProctoringProvider,
    StudentAllowance,
    User
)
from edx_exams.apps.core.statuses import ExamAttemptStatus
from edx_exams.apps.router.interop import get_active_exam_attempt

log = logging.getLogger(__name__)


class CourseExamsView(ExamsAPIView):
    """
    View for exams in a specific course.

    HTTP PATCH
    Given a list of exam data for a course, this view will either create a new exam (if one doesn't exist), or modify
    an existing exam. Any course exams missing from the request will be marked as inactive.

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

    HTTP GET
    Return a list of active exams for a course.

    **GET Response**
    Returns:
        * 200: OK, list of Exam Objects
    """

    authentication_classes = (JwtAuthentication,)
    permission_classes = (CourseStaffUserPermissions,)

    @classmethod
    def update_exam(cls, exam_object, fields):
        """
        Given an exam object, update to the given fields value
        """
        for attr, value in fields.items():
            setattr(exam_object, attr, value)
        exam_object.save()

        log.info(
            'Updated existing exam=%(exam_id)s',
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
            'Created new exam=%(exam_id)s',
            {
                'exam_id': exam.id,
            }
        )

    @classmethod
    def handle_exams(cls, request_exams_list, course_exams_qs, course_id):
        """
        Given a list of exams for the course, determine if we can update in place or
        if we need to create a new exam.
        """
        exams_by_content_id = {exam.content_id: exam for exam in course_exams_qs}

        for exam in request_exams_list:
            # should only be one object per exam type per content_id
            existing_exam = exams_by_content_id.get(exam['content_id'])

            if existing_exam and exam['exam_type'] == existing_exam.exam_type:
                # if the exam type is the same, update the existing exam
                update_fields = {
                    'exam_name': exam['exam_name'],
                    'time_limit_mins': exam['time_limit_mins'],
                    'due_date': exam['due_date'],
                    'hide_after_due': exam['hide_after_due'],
                    'is_active': exam['is_active'],
                }
                cls.update_exam(existing_exam, update_fields)
            else:
                # if the exam type is different, mark the existing exam as inactive
                # and create a new exam
                if existing_exam:
                    cls.update_exam(existing_exam, {'is_active': False})

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
            200: 'OK',
            400: 'Invalid request. See message.'
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
            course_exams = get_course_exams(course_id)

            # decide how to update or create exams based on the request and already existing exams
            self.handle_exams(request_exams, course_exams, course_id)

            # mark any exams not included in the request as inactive. The Query set has already been filtered by course
            remaining_exams = course_exams.exclude(content_id__in=[exam['content_id'] for exam in request_exams])
            remaining_exams.update(is_active=False)

            response_status = status.HTTP_200_OK
            data = {}
        else:
            response_status = status.HTTP_400_BAD_REQUEST
            data = {'detail': 'Invalid data', 'errors': serializer.errors}

        return Response(status=response_status, data=data)

    def get(self, request, course_id):
        """
        Return a list of all active exams given a course_id
        """
        course_exams = get_course_exams(course_id)
        serialized_exams = ExamSerializer(course_exams, many=True).data
        return Response(status=status.HTTP_200_OK, data=serialized_exams)


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
        'escalation_email': 'test@example.com',
    }

    HTTP PATCH
    Creates or updates a CourseExamConfiguration.
    Expected PATCH data: {
        'provider': 'test_provider',
        'escalation_email': 'test@example.com',
    }
    **PATCH data Parameters**
        * provider: This is the name of the selected proctoring provider for the course.
        * escalation_email: This is the email to which learners should send emails to escalate problems for the course.

    **Exceptions**
        * HTTP_400_BAD_REQUEST
    """

    authentication_classes = (JwtAuthentication,)
    permission_classes = (CourseStaffOrReadOnlyPermissions,)

    def get(self, request, course_id):
        """
        Get exam configuration for a course
        """
        try:
            configuration = CourseExamConfiguration.objects.get(course_id=course_id)
        except CourseExamConfiguration.DoesNotExist:
            # If configuration is set to None, then the provider is serialized to the empty string instead of None.
            configuration = {}

        serializer = CourseExamConfigurationReadSerializer(configuration)
        return Response(serializer.data)

    def patch(self, request, course_id):
        """
        Create/update course exam configuration.
        """
        serializer = CourseExamConfigurationWriteSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            create_or_update_course_exam_configuration(
                course_id,
                validated_data['provider'],
                validated_data['escalation_email'],
            )
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    def get_queryset(self):
        org_key = self.request.query_params.get('org', None)
        if org_key:
            return ProctoringProvider.objects.filter(Q(org_key=org_key) | Q(org_key=None))
        return ProctoringProvider.objects.all()


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
    permission_classes = (CourseStaffOrReadOnlyPermissions,)

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
        claims = {'course_id': exam.course_id, 'content_id': exam.content_id}
        expiration_window = 60
        exam_attempt = ExamAttempt.get_current_exam_attempt(user.id, exam.id)

        data = {'detail': 'Exam access token not granted'}
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
            log.info('Creating exam access token')
            access_token = sign_token_for(user.lms_user_id, expiration_window, claims)
            data = {'exam_access_token': access_token, 'exam_access_token_expiration': expiration_window}

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
                            data={'detail': 'Exam does not exist'})

        response = self.get_response(exam, request.user)

        return response


class LatestExamAttemptView(ExamsAPIView):
    """
    Endpoint for the fetching a user's latest exam attempt.
    /exams/attempt/latest

    Supports:
        HTTP GET: Get the data for a user's latest exam attempt.

    HTTP GET
    Fetches a user's latest exam attempt for a given exam.
    If no exam is provided, the actively running attempt is returned.
    Status changes to 'submitted' if time remaining is zero.

    **GET data Parameters**
        'user': The data of the user whose latest attempt we want to fetch.
        'exam_id': The id of the exam whose latest attempt we want to fetch.
        'content_id: (optional) If provided, return the state of the user's attempt
            for this exam regardless of state.

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
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        HTTP GET handler to fetch all exam attempt data

        TODO: The endpoint should be refactored on deprecation of edx-proctoring.
        Most of the complexity here has to do with the fact that we are supporting
        slightly different API behaviors from that service.

        Parameters:
            None

        Returns:
            A Response object containing all `ExamAttempt` data.
        """
        user = request.user
        exam_content_id = request.GET.get('content_id', None)
        exam = get_exam_by_content_id(exam_content_id)

        # if a specific exam is requested always return that exam
        if exam is not None:
            attempt = get_current_exam_attempt(user.id, exam.id)
        else:
            attempt = get_active_attempt_for_user(user.id)

        # if there is an active attempt in this service, return it.
        if attempt is not None:
            # An in progress attempt may be moved to 'submitted' if check_if_exam_timed_out
            # determines that the attempt has timed out.
            attempt = check_if_exam_timed_out(attempt)
            serialized_attempt = StudentAttemptSerializer(attempt)
            if attempt.status in (ExamAttemptStatus.started, ExamAttemptStatus.ready_to_submit):
                return Response(status=status.HTTP_200_OK, data=serialized_attempt.data)

        # if edx-proctoring has an active attempt, return it
        legacy_attempt, response_status = get_active_exam_attempt(user.lms_user_id)
        if (
            legacy_attempt is not None
            and legacy_attempt != {}
            and response_status == status.HTTP_200_OK
        ):
            return Response(status=status.HTTP_200_OK, data=legacy_attempt)

        # otherwise return the attempt from edx-exams regardless of status
        return Response(
            status=status.HTTP_200_OK,
            data=StudentAttemptSerializer(attempt).data if attempt else {}
        )


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
    permission_classes = (IsAuthenticated,)

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

        action_mapping = {}
        course_id = attempt.exam.course_id
        if request.user.is_staff or request.user.has_course_staff_permission(course_id):
            action_mapping = {
                'verify': ExamAttemptStatus.verified,
                'reject': ExamAttemptStatus.rejected,
            }
        # instructors/staff cannot take exams so they do not need these actions
        elif attempt.user.id == request.user.id:
            action_mapping = {
                'stop': ExamAttemptStatus.ready_to_submit,
                'start': ExamAttemptStatus.started,
                'submit': ExamAttemptStatus.submitted,
                'click_download_software': ExamAttemptStatus.download_software_clicked,
                'error': ExamAttemptStatus.error,
            }
        else:
            error_msg = (
                f'user_id={attempt.user.id} attempted to update attempt_id={attempt.id} in '
                f'course_id={course_id} but does not have access to it. (action={action})'
            )
            error = {'detail': error_msg}
            return Response(status=status.HTTP_403_FORBIDDEN, data=error)

        to_status = action_mapping.get(action)
        if to_status:
            attempt_id = update_attempt_status(attempt_id, to_status)
            data = {'exam_attempt_id': attempt_id}
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

    def delete(self, request, attempt_id):
        """
        HTTP DELETE handler to delete exam attempt
        """
        exam_attempt = get_attempt_by_id(attempt_id)
        if exam_attempt is None:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'detail': f'Attempt with attempt_id={attempt_id} does not exist.'}
            )

        if (
            exam_attempt.user.id != request.user.id and
            not request.user.is_staff and
            not request.user.has_course_staff_permission(exam_attempt.exam.course_id)
        ):
            error_msg = (
                f'user_id={exam_attempt.user.id} attempted to delete attempt_id={exam_attempt.id} in '
                f'course_id={exam_attempt.exam.course_id} but does not have access to it.'
            )
            error = {'detail': error_msg}
            return Response(status=status.HTTP_403_FORBIDDEN, data=error)

        reset_exam_attempt(exam_attempt, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class InstructorAttemptsListView(ExamsAPIView):
    """
    Endpoint for listing exam attempts. Used to provide data for the instructor
    facing exam dashboard.

    /instructor_view/attempts?exam_id=<exam_id>

    Supports:
        HTTP GET: List student exam attempts.
    """

    authentication_classes = (JwtAuthentication,)
    permission_classes = (CourseStaffUserPermissions,)

    def get(self, request, course_id):
        """
        HTTP GET handler to fetch all exam attempt data for a given exam.

        Query Parameters:
            exam_id: Unique identifier for an exam.

        Returns:
            A Response object containing all `ExamAttempt` data.
        """
        exam_id = request.query_params.get('exam_id', None)

        # permissions are checked at the course level, the requested
        # exam must be in the course the user has been authorized to access
        if get_exam_by_id(exam_id).course_id != course_id:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={'detail': 'Exam does not exist in course'}
            )

        # instructor serializer will follow FK relationships to get user and
        # exam fields. This list is potentially large so use
        # select related to avoid n+1 issues.
        attempts = get_exam_attempts(exam_id).select_related('exam', 'user')

        paginator = LimitOffsetPagination()
        paginated_attempts = paginator.paginate_queryset(attempts, request)
        return paginator.get_paginated_response(
            InstructorViewAttemptSerializer(paginated_attempts, many=True).data
        )


class CourseExamAttemptView(ExamsAPIView):
    """
    Endpoint for getting timed or proctored exam and its attempt data given the request user.
    /student/exam/attempt/course_id/{course_id}/content_id/{content_id}
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

    authentication_classes = (JwtAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, course_id, content_id):  # pylint: disable=unused-argument
        """
        HTTP GET handler. Returns exam and an attempt, if one exists for the exam
        """
        exam = get_exam_by_content_id(content_id)

        if exam is None:
            data = {'exam': {}}
            return Response(data)

        serialized_exam = ExamSerializer(exam).data
        allowance = StudentAllowance.get_allowance_for_user(request.user.id, exam.id)

        exam_type_class = get_exam_type(exam.exam_type)

        # the following are additional fields that the frontend expects
        serialized_exam['type'] = exam.exam_type
        serialized_exam['is_proctored'] = exam_type_class.is_proctored
        serialized_exam['is_practice_exam'] = exam_type_class.is_practice
        # timed exams will have None as a backend
        serialized_exam['backend'] = exam.provider.verbose_name if exam.provider is not None else None

        serialized_exam['passed_due_date'] = is_exam_passed_due(serialized_exam)

        if allowance is not None:
            serialized_exam['total_time'] = exam.time_limit_mins + allowance.extra_time_mins
        else:
            serialized_exam['total_time'] = exam.time_limit_mins

        exam_attempt = get_current_exam_attempt(request.user.id, exam.id)

        if exam_attempt is not None:
            exam_attempt = check_if_exam_timed_out(exam_attempt)

            student_attempt = StudentAttemptSerializer(exam_attempt).data
            serialized_exam['attempt'] = student_attempt
        else:
            serialized_exam['attempt'] = {}

        data = {'exam': serialized_exam}
        return Response(data)


class ProctoringSettingsView(ExamsAPIView):
    """
    Endpoint for getting a course/exam's proctoring settings, including course-wide settings like the escalation email
    and exam-specific settings like provider settings.

    exam/provider_settings/course_id/{course_id}/exam_id/{exam_id}

    Supports:
        HTTP GET:
            Returns proctoring configuration settings given an exam_id

            {
                provider_tech_support_email: '',
                provider_tech_support_phone: '',
                provider_tech_support_site: '',
                provider_name: 'test provider',
                escalation_name: 'test@example.com',
            }
    """

    authentication_classes = (JwtAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, course_id, exam_id):
        """
        HTTP GET handler. Returns exam configuration settings given an exam_id

        The course_id is provided as a path parameter to account for the exams ExamRequestMiddleware router.
        """
        provider = get_provider_by_exam_id(exam_id)
        config_data = get_course_exam_configuration_by_course_id(course_id)

        data = {}

        if provider:
            data['provider_tech_support_email'] = provider.tech_support_email
            data['provider_tech_support_phone'] = provider.tech_support_phone
            data['provider_tech_support_url'] = provider.tech_support_url
            data['provider_name'] = provider.verbose_name

        data['proctoring_escalation_email'] = config_data.escalation_email

        return Response(data)


class AllowanceView(ExamsAPIView):
    """
    Endpoint for the StudentAllowance

    /exams/course_id/{course_id}/allowances

    Supports:
        HTTP GET:
            Returns a list of allowances for a course.
        HTTP POST:
            Create one or more allowances

    Expected POST data: [{
        "username": "test_user",
        "exam_id": 1234,
        "extra_time_mins": 30,
    }]
    **POST data Parameters**
        * username OR email: username or email for which to create or update an allowance.
        * exam_id: ID of the exam for which to create or update an allowance
        * extra_time_mins: Extra time (in minutes) that a student is allotted for an exam.
    """

    authentication_classes = (JwtAuthentication,)
    permission_classes = (CourseStaffUserPermissions,)

    def get(self, request, course_id):
        """
        HTTP GET handler. Returns a list of allowances for a course.
        """
        allowances = StudentAllowance.get_allowances_for_course(course_id)
        return Response(AllowanceSerializer(allowances, many=True).data)

    def post(self, request, course_id):  # pylint: disable=unused-argument
        """
        HTTP POST handler. Creates allowances based on the given list.
        """
        allowances = request.data

        serializer = AllowanceSerializer(data=allowances, many=True)

        if serializer.is_valid():
            # We expect the number of allowances in each request to be small. Should they increase,
            # we should not query within the loop, and instead refactor this to optimize
            # the DB calls.
            allowance_objects = [
                StudentAllowance(
                    user=(
                        User.objects.get(username=allowance['username'])
                        if allowance.get('username')
                        else User.objects.get(email=allowance['email'])
                    ),
                    exam=Exam.objects.get(id=allowance['exam_id']),
                    extra_time_mins=allowance['extra_time_mins']
                )
                for allowance in allowances
            ]
            StudentAllowance.objects.bulk_create(
                allowance_objects,
                update_conflicts=True,
                unique_fields=['user', 'exam'],
                update_fields=['extra_time_mins']
            )

            return Response(status=status.HTTP_200_OK)
        else:
            response_status = status.HTTP_400_BAD_REQUEST
            data = {'detail': 'Invalid data', 'errors': serializer.errors}
            return Response(status=response_status, data=data)
