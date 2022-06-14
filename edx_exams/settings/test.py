import os

from edx_exams.settings.base import *

# IN-MEMORY TEST DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}
# END IN-MEMORY TEST DATABASE
JWT_AUTH.update(
    {
        "JWT_SECRET_KEY": SOCIAL_AUTH_EDX_OAUTH2_SECRET,
        "JWT_ISSUER": "https://test-provider/oauth2",
        "JWT_AUDIENCE": SOCIAL_AUTH_EDX_OAUTH2_KEY,
    }
)
