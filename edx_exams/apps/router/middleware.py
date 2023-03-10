"""
Middleware that checks if in incoming request should be
routed to the legacy proctoring service (edx-proctoring)
"""
import logging

from django.utils.deprecation import MiddlewareMixin

from edx_exams.apps.api.v1.views import CourseExamAttemptView, CourseExamsView
from edx_exams.apps.core.models import CourseExamConfiguration
from edx_exams.apps.router.views import CourseExamAttemptLegacyView, CourseExamsLegacyView

log = logging.getLogger(__name__)

LEGACY_VIEW_MAP = {
    CourseExamsView: CourseExamsLegacyView,
    CourseExamAttemptView: CourseExamAttemptLegacyView,
    # ExamAttemptView: ExamAttemptLegacyView,
}


class ExamRequestMiddleware(MiddlewareMixin):
    """
    Intercept requests and determine if exams for this course
    should be managed by legacy edx-proctoring system. If so, requests
    are intercepted and forwarded to that service
    """
    def process_view(self, request, view_func, view_args, view_kwargs):  # pylint: disable=missing-function-docstring
        try:
            legacy_view = LEGACY_VIEW_MAP.get(view_func.view_class)
        except AttributeError:      # pragma: no cover
            legacy_view = None

        # call into override if a function is defined for this request method
        if legacy_view and getattr(legacy_view, request.method.lower()):
            course_id = view_kwargs.get('course_id')
            course_configuration = CourseExamConfiguration.get_configuration_for_course(course_id)
            if not course_configuration or course_configuration.provider is None:
                log.info('Forwarding request to legacy edx-proctoring service for course %s', course_id)
                return legacy_view.as_view()(request=request, *view_args, **view_kwargs)

        return None
