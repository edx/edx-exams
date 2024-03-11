from edx_exams.settings.base import *

DEBUG = True

# CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
# END CACHE CONFIGURATION

# DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': root('default.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
# END DATABASE CONFIGURATION

# EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# END EMAIL CONFIGURATION

# TOOLBAR CONFIGURATION
# See: https://django-debug-toolbar.readthedocs.org/en/latest/installation.html
if os.environ.get('ENABLE_DJANGO_TOOLBAR', False):
    INSTALLED_APPS += (
        'debug_toolbar',
    )

    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    DEBUG_TOOLBAR_PATCH_SETTINGS = False

INTERNAL_IPS = ('127.0.0.1',)
# END TOOLBAR CONFIGURATION

# AUTHENTICATION
# Use a non-SSL URL for authorization redirects
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False

# Generic OAuth2 variables irrespective of SSO/backend service key types.
OAUTH2_PROVIDER_URL = 'http://localhost:18000/oauth2'

# OAuth2 variables specific to social-auth/SSO login use case.
SOCIAL_AUTH_EDX_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_EDX_OAUTH2_KEY', 'edx_exams-sso-key')
SOCIAL_AUTH_EDX_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_EDX_OAUTH2_SECRET', 'edx_exams-sso-secret')
SOCIAL_AUTH_EDX_OAUTH2_ISSUER = os.environ.get('SOCIAL_AUTH_EDX_OAUTH2_ISSUER', 'http://localhost:18000')
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = os.environ.get('SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT', 'http://localhost:18000')
SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL = os.environ.get('SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL', 'http://localhost:18000/logout')
SOCIAL_AUTH_EDX_OAUTH2_PUBLIC_URL_ROOT = os.environ.get(
    'SOCIAL_AUTH_EDX_OAUTH2_PUBLIC_URL_ROOT', 'http://localhost:18000',
)

# OAuth2 variables specific to backend service API calls.
BACKEND_SERVICE_EDX_OAUTH2_KEY = os.environ.get('BACKEND_SERVICE_EDX_OAUTH2_KEY', 'edx_exams-backend-service-key')
BACKEND_SERVICE_EDX_OAUTH2_SECRET = os.environ.get(
    'BACKEND_SERVICE_EDX_OAUTH2_SECRET',
    'edx_exams-backend-service-secret'
)

JWT_AUTH.update({
    'JWT_ALGORITHM': 'HS256',
    'JWT_SECRET_KEY': 'lms-secret',
    'JWT_ISSUER': 'http://localhost:18000/oauth2',
    'JWT_AUDIENCE': None,
    'JWT_VERIFY_AUDIENCE': False,
    'JWT_PUBLIC_SIGNING_JWK_SET': (
        '{"keys": [{"kid": "devstack_key", "e": "AQAB", "kty": "RSA", "n": "smKFSYowG6nNUAdeqH1jQQnH1PmIHphzBmwJ5vRf1vu'
        '48BUI5VcVtUWIPqzRK_LDSlZYh9D0YFL0ZTxIrlb6Tn3Xz7pYvpIAeYuQv3_H5p8tbz7Fb8r63c1828wXPITVTv8f7oxx5W3lFFgpFAyYMmROC'
        '4Ee9qG5T38LFe8_oAuFCEntimWxN9F3P-FJQy43TL7wG54WodgiM0EgzkeLr5K6cDnyckWjTuZbWI-4ffcTgTZsL_Kq1owa_J2ngEfxMCObnzG'
        'y5ZLcTUomo4rZLjghVpq6KZxfS6I1Vz79ZsMVUWEdXOYePCKKsrQG20ogQEkmTf9FT_SouC6jPcHLXw"}]}'
    ),
    'JWT_ISSUERS': [{
        'AUDIENCE': 'lms-key',
        'ISSUER': 'http://localhost:18000/oauth2',
        'SECRET_KEY': 'lms-secret',
    }],
})

# todo: create new non-test, private signing jwk
TOKEN_SIGNING.update({
    'JWT_PRIVATE_SIGNING_JWK': '''{
        "e": "AQAB",
        "d": "HIiV7KNjcdhVbpn3KT-I9n3JPf5YbGXsCIedmPqDH1d4QhBofuAqZ9zebQuxkRUpmqtYMv0Zi6ECSUqH387GYQF_XvFUFcjQRPycISd8\
        TH0DAKaDpGr-AYNshnKiEtQpINhcP44I1AYNPCwyoxXA1fGTtmkKChsuWea7o8kytwU5xSejvh5-jiqu2SF4GEl0BEXIAPZsgbzoPIWNxgO4_R\
        zNnWs6nJZeszcaDD0CyezVSuH9QcI6g5QFzAC_YuykSsaaFJhZ05DocBsLczShJ9Omf6PnK9xlm26I84xrEh_7x4fVmNBg3xWTLh8qOnHqGko9\
        3A1diLRCrKHOvnpvgQ",
        "n": "o5cn3ljSRi6FaDEKTn0PS-oL9EFyv1pI7dRgffQLD1qf5D6sprmYfWWokSsrWig8u2y0HChSygR6Jn5KXBqQn6FpM0dDJLnWQDRXHLl3\
        Ey1iPYgDSmOIsIGrV9ZyNCQwk03wAgWbfdBTig3QSDYD-sTNOs3pc4UD_PqAvU2nz_1SS2ZiOwOn5F6gulE1L0iE3KEUEvOIagfHNVhz0oxa_V\
        RZILkzV-zr6R_TW1m97h4H8jXl_VJyQGyhMGGypuDrQ9_vaY_RLEulLCyY0INglHWQ7pckxBtI5q55-Vio2wgewe2_qYcGsnBGaDNbySAsvYcW\
        RrqDiFyzrJYivodqTQ",
        "q": "3T3DEtBUka7hLGdIsDlC96Uadx_q_E4Vb1cxx_4Ss_wGp1Loz3N3ZngGyInsKlmbBgLo1Ykd6T9TRvRNEWEtFSOcm2INIBoVoXk7W5Ru\
        Pa8Cgq2tjQj9ziGQ08JMejrPlj3Q1wmALJr5VTfvSYBu0WkljhKNCy1KB6fCby0C9WE",
        "p": "vUqzWPZnDG4IXyo-k5F0bHV0BNL_pVhQoLW7eyFHnw74IOEfSbdsMspNcPSFIrtgPsn7981qv3lN_staZ6JflKfHayjB_lvltHyZxfl0\
        dvruShZOx1N6ykEo7YrAskC_qxUyrIvqmJ64zPW3jkuOYrFs7Ykj3zFx3Zq1H5568G0",
        "kid": "localdev_exam_token_key", "kty": "RSA"
    }''',
})

ENABLE_AUTO_AUTH = True

LOGGING = get_logger_config(debug=DEBUG)

SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_DOMAIN = 'localhost'

ROOT_URL = 'http://localhost:18740'
LTI_API_BASE = 'http://localhost:18740'
LMS_ROOT_URL = 'http://localhost:18000'
LEARNING_MICROFRONTEND_URL = 'http://localhost:2000'
LTI_CUSTOM_URL_CLAIM = 'http://localhost:2000'
EXAMS_DASHBOARD_MFE_URL = 'http://localhost:2020'

CORS_ORIGIN_WHITELIST = (
    'http://localhost:2001',
    LEARNING_MICROFRONTEND_URL,
    EXAMS_DASHBOARD_MFE_URL,
)

ALLOWED_HOSTS = ['*']

#####################################################################
# Lastly, see if the developer has any local overrides.
if os.path.isfile(join(dirname(abspath(__file__)), 'private.py')):
    from .private import *  # pylint: disable=import-error

# EVENT BUS
# Below are Django settings related to setting up the Open edX event bus.
# Because the event bus requires a Docker based networking layer, as included in devstack, the event bus does not work
# outside of a Docker container. Therefore, the settings related to networking are set to None, because this file is
# used for the local application server. However, because these local Django settings are also used by Tutor, we include
# sensible values for non-network related settings. Tutor users can override these settings when setting up the event
# bus, including the network-related settings.

EVENT_BUS_PRODUCER = 'edx_event_bus_kafka.create_producer'
EVENT_BUS_CONSUMER = 'edx_event_bus_kafka.KafkaEventConsumer'
EVENT_BUS_TOPIC_PREFIX = 'dev'
EVENT_BUS_KAFKA_SCHEMA_REGISTRY_URL = None
EVENT_BUS_KAFKA_BOOTSTRAP_SERVERS = None

attempt_submitted_event_config = EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.exam.attempt.submitted.v1']
attempt_submitted_event_config['learning-exam-attempt-lifecycle']['enabled'] = True

attempt_rejected_event_config = EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.exam.attempt.rejected.v1']
attempt_rejected_event_config['learning-exam-attempt-lifecycle']['enabled'] = True

attempt_verified_event_config = EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.exam.attempt.verified.v1']
attempt_verified_event_config['learning-exam-attempt-lifecycle']['enabled'] = True

attempt_errored_event_config = EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.exam.attempt.errored.v1']
attempt_errored_event_config['learning-exam-attempt-lifecycle']['enabled'] = True

attempt_reset_event_config = EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.exam.attempt.reset.v1']
attempt_reset_event_config['learning-exam-attempt-lifecycle']['enabled'] = True
