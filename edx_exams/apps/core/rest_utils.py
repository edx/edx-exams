"""
Utils for reading and writing data to other services using REST.
"""
from django.conf import settings
from edx_rest_api_client import client as rest_client
from requests.exceptions import HTTPError


# pylint: disable=inconsistent-return-statements
def make_request(method, url, client, **kwargs):
    """
    Helper method to make an http request using
    an authN'd client.
    """
    if method not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:  # pragma: no cover
        raise Exception('invalid http method: ' + method)

    response = client.request(method, url, **kwargs)

    if response.status_code >= 200 and response.status_code < 300:
        return response
    else:
        response.raise_for_status()


def get_client(host_base_url=settings.LMS_ROOT_URL):
    """
    Returns an authenticated edX REST API client.
    """
    client = rest_client.OAuthAPIClient(
        host_base_url,
        settings.BACKEND_SERVICE_EDX_OAUTH2_KEY,
        settings.BACKEND_SERVICE_EDX_OAUTH2_SECRET,
    )
    client._ensure_authentication()  # pylint: disable=protected-access
    if not client.auth.token:  # pragma: no cover
        raise Exception('No Auth Token')
    return client
