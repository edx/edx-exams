"""
Mixins for edx-exams API tests.
"""
from time import time

import jwt
from django.conf import settings

JWT_AUTH = "JWT_AUTH"


class JwtMixin:
    """
    Mixin with JWT-related helper functions
    """

    JWT_SECRET_KEY = getattr(settings, JWT_AUTH)["JWT_SECRET_KEY"]
    JWT_ISSUER = getattr(settings, JWT_AUTH)["JWT_ISSUER"]
    JWT_AUDIENCE = getattr(settings, JWT_AUTH)["JWT_AUDIENCE"]

    def generate_token(self, payload, secret=None):
        """
        Generate a JWT token with the provided payload
        """
        secret = secret or self.JWT_SECRET_KEY
        token = jwt.encode(payload, secret)
        return token

    def default_payload(self, user, ttl=1):
        """
        Generate a bare payload, in case tests need to manipulate
        it directly before encoding
        """
        now = int(time())

        return {
            "iss": self.JWT_ISSUER,
            "sub": user.pk,
            "aud": self.JWT_AUDIENCE,
            "nonce": "dummy-nonce",
            "exp": now + ttl,
            "iat": now,
            "preferred_username": user.username,
            "administrator": user.is_staff,
            "email": user.email,
            "locale": "en",
            "name": user.full_name,
            "given_name": "",
            "family_name": "",
        }
