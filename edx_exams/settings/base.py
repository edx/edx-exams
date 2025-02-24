import os
from os.path import abspath, dirname, join

from corsheaders.defaults import default_headers as corsheaders_default_headers

from edx_exams.settings.utils import get_logger_config

# PATH vars
PROJECT_ROOT = join(abspath(dirname(__file__)), "..")


def root(*path_fragments):
    return join(abspath(PROJECT_ROOT), *path_fragments)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('EDX_EXAMS_SECRET_KEY', 'insecure-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'edx_event_bus_kafka',
    'release_util',
    'drf_yasg',
    'edx_api_doc_tools',
    'lti_consumer.apps.LTIConsumerApp',
    'token_utils',
    'openedx_events',
)

THIRD_PARTY_APPS = (
    'corsheaders',
    'csrf.apps.CsrfAppConfig',  # Enables frontend apps to retrieve CSRF tokens
    'rest_framework',
    'rest_framework_swagger',
    'social_django',
    'waffle',
)

PROJECT_APPS = (
    'edx_exams.apps.core',
    'edx_exams.apps.api',
    'edx_exams.apps.lti',
)

INSTALLED_APPS += THIRD_PARTY_APPS
INSTALLED_APPS += PROJECT_APPS

MIDDLEWARE = (
    # Resets RequestCache utility for added safety.
    'edx_django_utils.cache.middleware.RequestCacheMiddleware',
    # Enables monitoring utility for writing custom metrics.
    'edx_django_utils.monitoring.middleware.MonitoringCustomMetricsMiddleware',
    'edx_django_utils.monitoring.DeploymentMonitoringMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'edx_rest_framework_extensions.auth.jwt.middleware.JwtAuthCookieMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'waffle.middleware.WaffleMiddleware',
    # Enables force_django_cache_miss functionality for TieredCache.
    'edx_django_utils.cache.middleware.TieredCacheMiddleware',
    # Outputs monitoring metrics for a request.
    'edx_rest_framework_extensions.middleware.RequestCustomAttributesMiddleware',
    # Ensures proper DRF permissions in support of JWTs
    'edx_rest_framework_extensions.auth.jwt.middleware.EnsureJWTAuthSettingsMiddleware',
    'edx_exams.apps.router.middleware.ExamRequestMiddleware'
)

REST_FRAMEWORK = {
    'PAGE_SIZE': 100
}

# Enable CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = corsheaders_default_headers + (
    'use-jwt-cookie',
)
CORS_ORIGIN_WHITELIST = []

ROOT_URLCONF = 'edx_exams.urls'

# This is the usage_id pattern. It's needed by the xblock-lti-consumer library, because some Django view URLs still
# use the usage_ids of components. For now, we include these here to support the use of the library. When the library
# is fully decoupled this can be removed. This setting is taken from edx-platform.
USAGE_ID_PATTERN = r'(?P<usage_id>(?:i4x://?[^/]+/[^/]+/[^/]+/[^@]+(?:@[^/]+)?)|(?:[^/]+))'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'edx_exams.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
# Set this value in the environment-specific files (e.g. local.py, production.py, test.py)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',  # Set to empty string for default.
    }
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Django 4.0+ uses zoneinfo if this is not set. We can remove this and
# migrate to zoneinfo after Django 4.2 upgrade. See more on following url
# https://docs.djangoproject.com/en/4.2/releases/4.0/#zoneinfo-default-timezone-implementation
USE_DEPRECATED_PYTZ = True

LOCALE_PATHS = (
    root('conf', 'locale'),
)

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = root('media')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'
# END MEDIA CONFIGURATION


# STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = root('assets')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    root('static'),
)

# EMAIL CONFIGURATION
DEFAULT_FROM_EMAIL = 'no-reply@example.com'

# TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/2.2/ref/settings/#templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': (
            root('templates'),
        ),
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'edx_exams.apps.core.context_processors.core',
            ),
            'debug': True,  # Django will only display debug pages if the global DEBUG setting is set to True.
        }
    },
]
# END TEMPLATE CONFIGURATION


# COOKIE CONFIGURATION
# The purpose of customizing the cookie names is to avoid conflicts when
# multiple Django services are running behind the same hostname.
# Detailed information at: https://docs.djangoproject.com/en/dev/ref/settings/
SESSION_COOKIE_NAME = 'edx_exams_sessionid'
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_NAME = 'edx_exams_csrftoken'
LANGUAGE_COOKIE_NAME = 'edx_exams_language'
# END COOKIE CONFIGURATION

CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = []

# AUTHENTICATION CONFIGURATION
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'

AUTH_USER_MODEL = 'core.User'

AUTHENTICATION_BACKENDS = (
    'auth_backends.backends.EdXOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

ENABLE_AUTO_AUTH = False
AUTO_AUTH_USERNAME_PREFIX = 'auto_auth_'

SOCIAL_AUTH_STRATEGY = 'auth_backends.strategies.EdxDjangoStrategy'

# Set these to the correct values for your OAuth2 provider (e.g., LMS)
SOCIAL_AUTH_EDX_OAUTH2_KEY = 'replace-me'
SOCIAL_AUTH_EDX_OAUTH2_SECRET = 'replace-me'
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = 'replace-me'
SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL = 'replace-me'
BACKEND_SERVICE_EDX_OAUTH2_KEY = 'replace-me'
BACKEND_SERVICE_EDX_OAUTH2_SECRET = 'replace-me'

JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_ISSUER': 'http://127.0.0.1:8000/oauth2',
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': lambda d: d.get('preferred_username'),
    'JWT_LEEWAY': 1,
    'JWT_DECODE_HANDLER': 'edx_rest_framework_extensions.auth.jwt.decoder.jwt_decode_handler',
    'JWT_PUBLIC_SIGNING_JWK_SET': None,
    'JWT_AUTH_COOKIE': 'edx-jwt-cookie',
    'JWT_AUTH_COOKIE_HEADER_PAYLOAD': 'edx-jwt-cookie-header-payload',
    'JWT_AUTH_COOKIE_SIGNATURE': 'edx-jwt-cookie-signature',
}

TOKEN_SIGNING = {
    'JWT_ISSUER': 'http://127.0.0.1:8740/',
    'JWT_SIGNING_ALGORITHM': 'RS512',
    'JWT_SUPPORTED_VERSION': '1.2.0',
    'JWT_PRIVATE_SIGNING_JWK': 'replace-me',
}

# Carry fields from the JWT token and LMS user into the local user
# Note: ENABLE_SET_REQUEST_USER_FOR_JWT_COOKIE applies a fix for
# https://github.com/jpadilla/django-rest-framework-jwt/issues/45
# However, we cannot use it in this service since the session user may
# differ from the JWT user when performing LTI launches with multiple accounts
# in the same browser.
EDX_DRF_EXTENSIONS = {
    "JWT_PAYLOAD_USER_ATTRIBUTE_MAPPING": {
        "administrator": "is_staff",
        "email": "email",
        "full_name": "full_name",
        "user_id": "lms_user_id",
    },
    "OAUTH2_USER_INFO_URL": "http://127.0.0.1:8000/oauth2/user_info",
    "ENABLE_SET_REQUEST_USER_FOR_JWT_COOKIE": False,
}

# Request the user's permissions in the ID token
EXTRA_SCOPE = ['permissions']

# TODO Set this to another (non-staff, ideally) path.
LOGIN_REDIRECT_URL = '/admin/'

LMS_ROOT_URL = None
# END AUTHENTICATION CONFIGURATION


# OPENEDX-SPECIFIC CONFIGURATION
PLATFORM_NAME = 'Your Platform Name Here'
# END OPENEDX-SPECIFIC CONFIGURATION

# Set up logging for development use (logging to stdout)
LOGGING = get_logger_config(debug=DEBUG)

LEARNING_MICROFRONTEND_URL = None

EXAMS_DASHBOARD_MFE_URL = None

LTI_CUSTOM_URL_CLAIM = None

# Event Bus Settings
EXAM_ATTEMPT_EVENTS_KAFKA_TOPIC_NAME = 'learning-exam-attempt-lifecycle'

# disable indexing on history_date
SIMPLE_HISTORY_DATE_INDEX = False

EVENT_BUS_PRODUCER_CONFIG = {
    'org.openedx.learning.exam.attempt.submitted.v1': {
        'learning-exam-attempt-lifecycle':
            {'event_key_field': 'exam_attempt.course_key', 'enabled': False},
    },
    'org.openedx.learning.exam.attempt.rejected.v1': {
        'learning-exam-attempt-lifecycle':
            {'event_key_field': 'exam_attempt.course_key', 'enabled': False},
    },
    'org.openedx.learning.exam.attempt.verified.v1': {
        'learning-exam-attempt-lifecycle':
            {'event_key_field': 'exam_attempt.course_key', 'enabled': False},
    },
    'org.openedx.learning.exam.attempt.errored.v1': {
        'learning-exam-attempt-lifecycle':
            {'event_key_field': 'exam_attempt.course_key', 'enabled': False},
    },
    'org.openedx.learning.exam.attempt.reset.v1': {
        'learning-exam-attempt-lifecycle':
            {'event_key_field': 'exam_attempt.course_key', 'enabled': False},
    },
}
