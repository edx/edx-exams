"""
LTI URLs
"""

from django.urls import path

from . import views

app_name = 'lti'
urlpatterns = [
    path('end_assessment/<int:attempt_id>', views.end_assessment),
    path('start_proctoring/<int:attempt_id>', views.start_proctoring, name='start_proctoring'),
]
