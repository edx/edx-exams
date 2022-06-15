"""
Factories for exams tests
"""

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    """
    Factory to create users to be used in other unit tests
    """

    class Meta:
        model = get_user_model()
        django_get_or_create = (
            "email",
            "username",
        )

    _DEFAULT_PASSWORD = "test"

    username = factory.Sequence("user{}".format)
    email = factory.Sequence("user+test+{}@edx.org".format)
    password = factory.PostGenerationMethodCall("set_password", _DEFAULT_PASSWORD)
    first_name = factory.Sequence("User{}".format)
    last_name = "Test"
    is_superuser = False
    is_staff = False
