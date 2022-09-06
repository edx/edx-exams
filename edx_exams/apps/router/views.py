import json
import logging

from django.http import HttpResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import status
from rest_framework.views import APIView

from edx_exams.apps.api.permissions import StaffUserPermissions
from edx_exams.apps.core.exam_types import get_exam_type
from edx_exams.apps.router.interop import register_exams

log = logging.getLogger(__name__)


class CourseExamsLegacyView(APIView):
    """
    View to create or modify exams for a course.

    Forwards all requests to edx-proctoring
    """
    authentication_classes = (JwtAuthentication,)
    permission_classes = (StaffUserPermissions,)

    def patch(self, request, course_id):
        exam_list = json.loads(request.body)

        # edx-proctoring does not support exam type so convert to
        # individual properties
        for exam in exam_list:
            exam_type = get_exam_type(exam.get('exam_type'))
            if exam_type:
                exam['is_proctored'] = exam_type.is_proctored
                exam['is_practice_exam'] = exam_type.is_practice

        response = register_exams(course_id, exam_list)
        response_data = response.json()

        if response.status_code != status.HTTP_200_OK:
            log.error(f'Failed to publish exams for course_id {course_id} response was {response_data}')

        return HttpResponse(
            content=response,
            content_type='application/json',
            status=response.status_code
        )
