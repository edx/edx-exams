"""
Core Application Configuration
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Application configuration for core application.
    """
    name = 'edx_exams.apps.core'

    def ready(self):
        """
        Connect handlers to signals.
        """
        from .signals import handlers  # pylint: disable=unused-import,import-outside-toplevel
