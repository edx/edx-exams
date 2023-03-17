"""
Views to wrap interactions with the legacy proctoring plugin
at https://github.com/openedx/edx-proctoring
"""
import json
import logging

from django.http import JsonResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from edx_exams.apps.api.permissions import StaffUserPermissions
from edx_exams.apps.core.exam_types import get_exam_type
from edx_exams.apps.router.interop import get_student_exam_attempt_data, register_exams

log = logging.getLogger(__name__)


class CourseExamsLegacyView(APIView):
    """
    View to create or modify exams for a course.

    Forwards all requests to edx-proctoring
    """
    authentication_classes = (JwtAuthentication,)
    permission_classes = (StaffUserPermissions,)

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

        response_data, status = register_exams(course_id, exam_list)

        return JsonResponse(
            data=response_data,
            status=status,
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
        response_data, status = get_student_exam_attempt_data(course_id, content_id, request.user.lms_user_id)

        return JsonResponse(
            data=response_data.get('exam', response_data),
            status=status,
            safe=False,
        )
