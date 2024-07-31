""" API v1 URLs. """

from django.urls import path, re_path

from edx_exams.apps.api.v1.views import (
    AllowanceView,
    CourseExamAttemptView,
    CourseExamConfigurationsView,
    CourseExamsView,
    ExamAccessTokensView,
    ExamAttemptView,
    InstructorAttemptsListView,
    LatestExamAttemptView,
    ProctoringProvidersView,
    ProctoringSettingsView
)
from edx_exams.apps.core.constants import COURSE_ID_PATTERN, EXAM_ID_PATTERN, USAGE_KEY_PATTERN

app_name = 'v1'

urlpatterns = [
    re_path(
        fr'exams/course_id/{COURSE_ID_PATTERN}/allowances/(?P<allowance_id>\d+)',
        AllowanceView.as_view(),
        name='course-allowance'
    ),
    re_path(
        fr'exams/course_id/{COURSE_ID_PATTERN}/allowances',
        AllowanceView.as_view(),
        name='course-allowances'
    ),
    re_path(
        fr'exams/course_id/{COURSE_ID_PATTERN}',
        CourseExamsView.as_view(),
        name='exams-course_exams'
    ),
    re_path(
        fr'configs/course_id/{COURSE_ID_PATTERN}',
        CourseExamConfigurationsView.as_view(),
        name='course-exam-config'
    ),
    re_path(
        r'^providers?$',
        ProctoringProvidersView.as_view(),
        name='proctoring-providers-list',
    ),
    re_path(
        fr'access_tokens/exam_id/{EXAM_ID_PATTERN}',
        ExamAccessTokensView.as_view(),
        name='exam-access-tokens'
    ),
    path(
        'exams/attempt/<int:attempt_id>',
        ExamAttemptView.as_view(),
        name='exams-attempt',
    ),
    path(
        'exams/attempt',
        ExamAttemptView.as_view(),
        name='exams-attempt',
    ),
    path(
        'exams/attempt/latest',
        LatestExamAttemptView.as_view(),
        name='exams-attempt-latest',
    ),
    re_path(
        fr'instructor_view/course_id/{COURSE_ID_PATTERN}/attempts',
        InstructorAttemptsListView.as_view(),
        name='instructor-attempts-list'
    ),
    re_path(
        fr'student/exam/attempt/course_id/{COURSE_ID_PATTERN}/content_id/{USAGE_KEY_PATTERN}',
        CourseExamAttemptView.as_view(),
        name='student-course_exam_attempt'
    ),
    re_path(
        fr'exam/provider_settings/course_id/{COURSE_ID_PATTERN}/exam_id/{EXAM_ID_PATTERN}',
        ProctoringSettingsView.as_view(),
        name='proctoring-settings'
    ),
]
