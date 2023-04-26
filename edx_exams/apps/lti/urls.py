"""
LTI URLs
"""

from django.urls import path

from . import views

app_name = 'lti'
urlpatterns = [
    path('acs_endpoint/<int:lti_config_id>', views.acs_endpoint, name='acs_endpoint'),
    path('end_assessment/<int:attempt_id>', views.end_assessment, name='end_assessment'),
    path('start_proctoring/<int:attempt_id>', views.start_proctoring, name='start_proctoring'),
]
