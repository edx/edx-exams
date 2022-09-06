"""
Module for writing data to edx-proctoring
"""
from posixpath import join as urljoin

from django.conf import settings
from requests.exceptions import HTTPError

from edx_exams.apps.core.rest_utils import get_client, make_request

LMS_REGISTER_PROCTORED_EXAMS_API_TPL = 'api/edx_proctoring/v1/proctored_exam/exam_registration/course_id/{}'

def register_exams(course_id, exam_list):
    path = LMS_REGISTER_PROCTORED_EXAMS_API_TPL.format(course_id)
    url = urljoin(settings.LMS_ROOT_URL, path)
    client = get_client(settings.LMS_ROOT_URL)
    try:
        response = make_request('PATCH', url, client, json=exam_list)
    except HTTPError as e:
        response = e.response
    return response
