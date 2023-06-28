"""
LTI URLs
"""

from django.urls import path

from . import views

app_name = 'lti'
urlpatterns = [
    path('<int:lti_config_id>/acs', views.acs, name='acs'),
    path('end_assessment/<int:attempt_id>', views.end_assessment, name='end_assessment'),
    path('start_proctoring/<int:attempt_id>', views.start_proctoring, name='start_proctoring'),
    path('exam/<int:exam_id>/instructor_tool', views.launch_instructor_tool, name='instructor_tool'),
]
