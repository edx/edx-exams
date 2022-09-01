"""
Middleware that checks if in incoming request should be
routed to the legacy proctoring service (edx-proctoring)
"""
from django.utils.deprecation import MiddlewareMixin

from edx_exams.apps.api.v1.views import CourseExamsView
from edx_exams.apps.core.models import CourseExamConfiguration
from edx_exams.apps.router.views import CourseExamsOverrideView

OVERRIDE_VIEW_MAP = {
    CourseExamsView: CourseExamsOverrideView
}

class ExamRequestMiddleware(MiddlewareMixin):
    """
    Intercept requests and determine if exams for this course
    should be managed by legacy edx-proctoring system. If so, requests
    are intercepted and forwarded to that service
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            override_view = OVERRIDE_VIEW_MAP.get(view_func.view_class)
        except AttributeError:
            override_view = None

        # call into override if a function is defined for this request method
        if override_view and getattr(override_view, request.method.lower()):
            course_id = view_kwargs.get('course_id')
            course_configuration = CourseExamConfiguration.get_configuration_for_course(course_id)
            if not course_configuration or course_configuration.provider is None:
                return override_view.as_view()(request=request, *view_args, **view_kwargs)
