"""
V1 API Views
"""
import logging
import uuid

from django.core.exceptions import ObjectDoesNotExist
from edx_api_doc_tools import path_parameter, schema
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from edx_exams.apps.api.permissions import StaffUserPermissions
from edx_exams.apps.api.serializers import ExamSerializer, ProctoringProviderSerializer
from edx_exams.apps.core.exam_types import get_exam_type
from edx_exams.apps.core.models import CourseExamConfiguration, Exam, ProctoringProvider

log = logging.getLogger(__name__)


class CourseExamsView(APIView):
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
                config = CourseExamConfiguration.objects.filter(course_id=course_id).first()

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


class CourseExamConfigurationsView(APIView):
    """
    View to create and update course exam configs for a specific course.

    Given a course id and a proctoring provider name, this view will either create a new course exam configuration
    (if one doesn't exist), or modify the proctoring provider on an existing course exam config.

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
    permission_classes = (StaffUserPermissions,)

    @classmethod
    def handle_config(cls, provider, course_id):
        """
        Helper method that decides whether to update existing or create new config.
        """
        CourseExamConfiguration.objects.update_or_create(
            course_id=course_id,
            defaults={'provider': provider})
        log.info(f"Created or updated course exam configuration course_id={course_id},provider={provider.name}")

    def patch(self, request, course_id):
        """
        Create/update course exam configuration.
        """
        # check that proctoring provider is in request
        if request.data.get('provider') is None:
            response_status = status.HTTP_400_BAD_REQUEST
            data = {"detail": "No proctoring provider name in request."}
        else:
            try:
                provider = ProctoringProvider.objects.get(name=request.data['provider'])
                self.handle_config(provider, course_id)
                response_status = status.HTTP_204_NO_CONTENT
                data = {}
            # return 400 if proctoring provider does not exist
            except ObjectDoesNotExist:
                response_status = status.HTTP_400_BAD_REQUEST
                data = {"detail": "Proctoring provider does not exist."}

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
