"""
LTI Apps
"""

from django.apps import AppConfig


class LtiConfig(AppConfig):
    """
    AppConfig for lti Djangoapp.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'edx_exams.apps.lti'

    def ready(self):
        from edx_exams.apps.lti.signals import handlers  # pylint: disable=import-outside-toplevel,unused-import
