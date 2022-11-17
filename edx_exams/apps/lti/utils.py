"""
LTI Utility Functions
"""
from django.conf import settings


def get_lti_root():
    if hasattr(settings, 'LTI_ROOT_URL_OVERRIDE'):
        return settings.LTI_ROOT_URL_OVERRIDE
    else:
        return settings.ROOT_URL
