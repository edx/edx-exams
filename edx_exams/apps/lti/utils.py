"""
LTI Utility Functions
"""
from django.conf import settings


def get_lti_root():
    return settings.ROOT_URL
