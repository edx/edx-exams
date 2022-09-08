"""
Module for writing data to edx-proctoring
"""
from posixpath import join as urljoin

from django.conf import settings
from requests.exceptions import HTTPError

from edx_exams.apps.core.rest_utils import get_client, make_request

LMS_PROCTORING_PLUGIN_BASE_PATH = 'api/edx_proctoring/v1/'
LMS_REGISTER_PROCTORED_EXAMS_API_TPL = 'proctored_exam/exam_registration/course_id/{}'


def register_exams(course_id, exam_list):
    """
    Register a list of course exams with the legacy proctoring service
    """
    path = LMS_REGISTER_PROCTORED_EXAMS_API_TPL.format(course_id)
    url = _proctoring_api_url(path)
    client = get_client(settings.LMS_ROOT_URL)
    try:
        response = make_request('PATCH', url, client, json=exam_list)
    except HTTPError as e:
        response = e.response
    return response


def _proctoring_api_url(path):
    """ Get proctoring plugin API url """
    full_path = LMS_PROCTORING_PLUGIN_BASE_PATH + path
    return urljoin(settings.LMS_ROOT_URL, full_path)
