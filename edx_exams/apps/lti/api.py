"""
LTI API
"""

from django.conf import settings
from lti_consumer.lti_1p3.consumer import LtiAdvantageConsumer
from lti_consumer.models import LtiConfiguration


def get_lti1p3_consumer():
    """
    Returns an configured instance of LTI consumer.
    """
    # TODO: We need a better look up than a hard-coded primary key. This will be
    #       informed by how we decide to store LTI configuration.
    lti_config = LtiConfiguration.objects.get(pk=1)
    return LtiAdvantageConsumer(
      # configuration provided by the LTI tool
      lti_oidc_url=lti_config.lti_1p3_oidc_url,
      lti_launch_url=lti_config.lti_1p3_launch_url,
      # platform and deployment configuration provided by the platform
      iss=settings.LMS_ROOT_URL,
      client_id=lti_config.lti_1p3_client_id,
      deployment_id="1",
      # platform asymmetric public key configuration
      rsa_key=lti_config.lti_1p3_private_key,
      rsa_key_id=lti_config.lti_1p3_private_key_id,
      # tool asymmetric public key configuration
      tool_key=lti_config.lti_1p3_tool_public_key,
      tool_keyset_url=lti_config.lti_1p3_tool_keyset_url
    )


def get_lti_preflight_url(lti_message_hint):
    lti_consumer = get_lti1p3_consumer()
    context = lti_consumer.prepare_preflight_url(lti_hint=lti_message_hint)
    return context


def get_resource_link():  # pylint: disable=missing-function-docstring
    # TODO: The resource link should uniquely represent the assessment in the Assessment Platform.
    # TODO: We SHOULD provide a value for the title attribute.
    # TODO: It's RECOMMENDED to provide a value for the description attribute.
    # TODO: The xblock-lti-consumer library does not currently support setting these attributes.
    return 'edx:proctored_exam:12345'


def get_optional_user_identity_claims():
    # These claims are optional.
    # TODO: This will need to have additional consideration for PII.
    return {
        'given_name': 'Michael',
        'family_name': 'Roytman',
        'name': 'Michael Roytman',
        'email': 'michaelroytman@example.com',
        'email_verified': True,
        'picture': 'example.com/michaelroytman.jpg',
        'locale': 'en_US'
    }
