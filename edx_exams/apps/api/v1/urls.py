""" API v1 URLs. """

from django.urls import re_path

from edx_exams.apps.api.v1.views import CourseExamsView
from edx_exams.apps.core.constants import COURSE_ID_PATTERN

app_name = 'v1'

urlpatterns = [
    re_path(fr'exams/course_id/{COURSE_ID_PATTERN}', CourseExamsView.as_view(), name='exams-course_exams'),
]
