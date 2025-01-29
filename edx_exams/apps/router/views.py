"""
Views to wrap interactions with the legacy proctoring plugin
at https://github.com/openedx/edx-proctoring
"""
import json
import logging

from django.http import JsonResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from edx_exams.apps.api.permissions import CourseStaffUserPermissions
from edx_exams.apps.core.exam_types import get_exam_type
from edx_exams.apps.router.interop import (
    get_provider_settings,
    get_student_exam_attempt_data,
    get_user_onboarding_data,
    register_exams
)

log = logging.getLogger(__name__)


class CourseExamsLegacyView(APIView):
    """
    View to create or modify exams for a course.

    Forwards all requests to edx-proctoring
    """
    authentication_classes = (JwtAuthentication,)
    permission_classes = (CourseStaffUserPermissions,)

    def patch(self, request, course_id):
        """
        Create or update a list of exams in edx-proctoring.
        """
        exam_list = json.loads(request.body)

        # edx-proctoring does not support exam type so convert to
        # individual properties
        for exam in exam_list:
            exam_type = get_exam_type(exam.get('exam_type'))
            if exam_type:
                exam['is_proctored'] = exam_type.is_proctored
                exam['is_practice_exam'] = exam_type.is_practice

        response_data, response_status = register_exams(course_id, exam_list)

        return JsonResponse(
            data=response_data,
            status=response_status,
            safe=False,
        )

    def get(self, request, course_id):  # pylint: disable=unused-argument
        """
        Currently unsupported endpoint
        """
        return JsonResponse(
            data=[],
            status=status.HTTP_404_NOT_FOUND,
            safe=False,
        )


class CourseExamAttemptLegacyView(APIView):
    """
    View to handle attempts for exams managed by edx-proctoring.
    """
    authentication_classes = (JwtAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, course_id, content_id):
        """
        Get exam and attempt data for user in a given section. Pass through
        the response from edx-proctoring directly.
        """
        response_data, response_status = get_student_exam_attempt_data(course_id, content_id, request.user.lms_user_id)

        # remove active_attempt to keep response consistent with CourseExamAttemptView
        if 'active_attempt' in response_data:
            del response_data['active_attempt']

        return JsonResponse(
            data=response_data,
            status=response_status,
            safe=False,
        )


class ProctoringSettingsLegacyView(APIView):
    """
    View to handle provider settings for exams managed by edx-proctoring
    """
    authentication_classes = (JwtAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, course_id, exam_id):  # pylint: disable=unused-argument
        """
        Get provider settings given an exam ID. Pass through the response from edx-proctoring directly
        """
        response_data, response_status = get_provider_settings(exam_id)

        return JsonResponse(
            data=response_data,
            status=response_status,
            safe=False
        )


class UserOnboardingLegacyView(APIView):
    """
    View to handle user onboarding for exams managed by edx-proctoring
    """
    authentication_classes = (JwtAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, course_id):
        """
        Get user onboarding data given course_id and an optional username
        """
        username = request.GET.get('username')

        response_data, response_status = get_user_onboarding_data(course_id, username)

        return JsonResponse(
            data=response_data,
            status=response_status,
            safe=False
        )
