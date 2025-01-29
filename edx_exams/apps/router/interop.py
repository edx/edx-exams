"""
Module for writing data to edx-proctoring
"""
import logging
from posixpath import join as urljoin
from urllib.parse import quote_plus

from django.conf import settings
from requests.exceptions import HTTPError
from rest_framework import status
from simplejson import JSONDecodeError

from edx_exams.apps.core.rest_utils import get_client, make_request

LMS_PROCTORING_PLUGIN_BASE_PATH = 'api/edx_proctoring/v1/'
LMS_REGISTER_PROCTORED_EXAMS_API_TPL = 'proctored_exam/exam_registration/course_id/{}'
LMS_PROCTORED_EXAM_ACTIVE_ATTEMPT_API_TPL = 'proctored_exam/active_attempt?user_id={}'
LMS_PROCTORED_EXAM_ATTEMPT_DATA_API_TPL = 'proctored_exam/attempt/course_id/{}?content_id={}&user_id={}'
LMS_PROCTORED_EXAM_ATTEMPT_API = 'proctored_exam/attempt'
LMS_PROCTORED_EXAM_PROVIDER_SETTINGS_API_TPL = 'proctored_exam/settings/exam_id/{}/'
LMS_PROCTORED_EXAM_ONBOARDING_DATA_API_TPL = 'user_onboarding/status?is_learning_mfe=true&course_id={}'

log = logging.getLogger(__name__)


def register_exams(course_id, exam_list):
    """
    Register a list of course exams with the legacy proctoring service
    """
    path = LMS_REGISTER_PROCTORED_EXAMS_API_TPL.format(course_id)
    response = _make_proctoring_request(path, 'PATCH', exam_list)

    response_data = _get_json_data(response)
    if response.status_code != status.HTTP_200_OK:
        log.error(
            f'Failed to publish exams for course_id {course_id} '
            f'got status={response.status_code} content={response.content}'
        )

    return response_data, response.status_code


def get_student_exam_attempt_data(course_id, content_id, lms_user_id):
    """
    Get student exam attempt data from the legacy proctoring service
    """
    content_id_url_safe = quote_plus(content_id)    # because this goes in the query string
    path = LMS_PROCTORED_EXAM_ATTEMPT_DATA_API_TPL.format(course_id, content_id_url_safe, lms_user_id)
    response = _make_proctoring_request(path, 'GET')

    response_data = _get_json_data(response)
    if response.status_code != status.HTTP_200_OK:
        log.error(f'Failed to get student attempt, response was {response.content}')

    return response_data, response.status_code


def get_active_exam_attempt(lms_user_id):
    """
    Get the active exam attempt for a user
    """
    path = LMS_PROCTORED_EXAM_ACTIVE_ATTEMPT_API_TPL.format(lms_user_id)
    response = _make_proctoring_request(path, 'GET')

    response_data = _get_json_data(response)
    if response.status_code != status.HTTP_200_OK:
        log.error(f'Failed to get active exam attempt, response was {response.content}')

    return response_data, response.status_code


def get_provider_settings(exam_id):
    """
    Get the provider settings for an exam given the exam id
    """
    path = LMS_PROCTORED_EXAM_PROVIDER_SETTINGS_API_TPL.format(exam_id)
    response = _make_proctoring_request(path, 'GET')

    response_data = _get_json_data(response)
    if response.status_code != status.HTTP_200_OK:
        log.error(f'Failed to get provider settings, response was {response.content}')

    return response_data, response.status_code


def get_user_onboarding_data(course_id, username=None):
    """
    Get user onboarding data given a course_id and optional username
    """
    template = LMS_PROCTORED_EXAM_ONBOARDING_DATA_API_TPL
    url_safe_course_id = quote_plus(course_id)

    if username:
        template += '&username={}'
        url_safe_username = quote_plus(username)
        path = template.format(url_safe_course_id, url_safe_username)
    else:
        path = template.format(url_safe_course_id)

    response = _make_proctoring_request(path, 'GET')

    response_data = _get_json_data(response)
    if response.status_code != status.HTTP_200_OK:
        log.error(f'Failed to get onboarding data, response was {response.content}')

    return response_data, response.status_code


def _make_proctoring_request(path, method, data=None):
    """ Make request to proctoring service """
    url = _proctoring_api_url(path)
    client = get_client(settings.LMS_ROOT_URL)
    try:
        response = make_request(method, url, client, json=data)
    except HTTPError as e:
        response = e.response
    return response


def _proctoring_api_url(path):
    """ Get proctoring plugin API url """
    full_path = LMS_PROCTORING_PLUGIN_BASE_PATH + path
    return urljoin(settings.LMS_ROOT_URL, full_path)


def _get_json_data(response):
    """
    Get the JSON data from a response
    """
    try:
        return response.json()
    except JSONDecodeError:      # pragma: no cover
        return {'data': 'Invalid JSON response received from edx-proctoring'}
