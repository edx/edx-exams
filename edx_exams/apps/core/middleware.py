"""
Middleware that checks if in incoming request has a browser jwt cookie
and enables JWT auth for that request.

This is a temporary workaround that allows easier testing of browser endpoints in
absence of a frontend UI. Normally a frontend application must explicity request
the JWT token to be used for auth by setting USE_JWT_COOKIE_HEADER.
"""
from django.utils.deprecation import MiddlewareMixin
from edx_rest_framework_extensions.auth.jwt.constants import USE_JWT_COOKIE_HEADER
from edx_rest_framework_extensions.auth.jwt.cookies import jwt_cookie_header_payload_name


class ForceJWTAuthMiddleware(MiddlewareMixin):  # pragma: no cover
    """ Middleware to automically enable JWT auth for browser requests """
    def process_request(self, request):  # pylint: disable=missing-function-docstring
        # prevent lti callback endpoints from reading jwt, we want to ensure
        # the session token generated for these is used instead
        if request.path.startswith('/lti/lti_consumer'):
            return

        if request.COOKIES.get(jwt_cookie_header_payload_name(), None):
            request.META[USE_JWT_COOKIE_HEADER] = "true"
