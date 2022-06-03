from urllib.parse import urljoin

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from lti_consumer.lti_1p3.exceptions import (
    BadJwtSignature,
    InvalidClaimValue,
    MalformedJwtToken,
    MissingRequiredClaim,
    NoSuitableKeys,
    TokenSignatureExpired,
    UnauthorizedToken,
)

from edx_exams.apps.lti.api import (
    get_lti1p3_consumer,
    get_lti_preflight_url,
    get_resource_link,
    get_optional_user_identity_claims,
)

def start_proctoring(request):
    """
    This view represents a "Platform-Originating Message"; the Assessment Platform is directing the browser to send a 
    "start proctoring" message to the Proctoring Tool. Because the Assessment Platform acts as the identity provider
    (IdP), it must follow the "OpenID Connect Launch Flow". The first step is the third-party initiated login; it is a
    "third-party" initiated login to protect against login CSRF attacks.

    "In 3rd party initiated login, the login flow is initiated by an OpenID Provider or another party, rather than the
    Relying Party. In this case, the initiator redirects to the Relying Party at its login initiation endpoint, which
    requests that the Relying Party send an Authentication Request to a specified OpenID Provider."
    https://www.imsglobal.org/spec/security/v1p0/#openid_connect_launch_flow
    
    This view redirects the learner's browser to the Proctoring Tool's initial OIDC login initiation URL, which acts as
    the first step of third-party initiated login. The Proctoring Tool should redirect the learner's browser to the
    Assessment Platform's "OIDC Authorization end-point", which starts the OpenID Connect authentication flow,
    implemented by the authenticate view.

    The Assessment Platform needs to know the Proctoring Tool's OIDC login initiation URL.
    The Proctoring Tool needs to know the Assessment Platform's OIDC authorization URL.
    This information is exchanged out-of-band during the registration phase.
    """
    # TODO: Here we'd do all the start of proctoring things

    lti_message_hint = 'LtiStartProctoring'
    preflight_url = get_lti_preflight_url(lti_message_hint)

    return redirect(preflight_url)

def end_assessment(request):
    """
    This view represents a "Platform-Originating Message"; the Assessment Platform is directing the browser to send a 
    "end assessment" message to the Proctoring Tool. Because the Assessment Platform acts as the identity provider
    (IdP), it must follow the "OpenID Connect Launch Flow". The first step is the third-party initiated login; it is a
    "third-party" initiated login to protect against login CSRF attacks.

    "In 3rd party initiated login, the login flow is initiated by an OpenID Provider or another party, rather than the
    Relying Party. In this case, the initiator redirects to the Relying Party at its login initiation endpoint, which
    requests that the Relying Party send an Authentication Request to a specified OpenID Provider."
    https://www.imsglobal.org/spec/security/v1p0/#openid_connect_launch_flow
    
    This view redirects the learner's browser to the Proctoring Tool's initial OIDC login initiation URL, which acts as
    the first step of third-party initiated login. The Proctoring Tool should redirect the learner's browser to the 
    Assessment Platform's "OIDC Authorization end-point", which starts the OpenID Connect authentication flow,
    implemented by the authenticate view.

    The Assessment Platform needs to know the Protoring Tool's OIDC login initiation URL.
    The Proctoring Tool needs to know the Assessment Platform's OIDC authorization URL.
    This information is exchanged out-of-band during the registration phase.
    """
    # TODO: Here we'd do all the end of assessment things.

    # TODO: "If the assessment needs to close due to an error NOT handled by the Assessment Platform
    #       that error MUST be passed along using the LtiEndAssessment message and the errormsg and errorlog claims.
    #       The message utilizes the OpenID connect workflow prior to sending the message."
    #       See 4.4 End Assessment Message.
    # TODO: I'm unsure whether the above requires that we send this message with the errormsg and errorlog claims
    #       if end_assessment_return was not specified in the request to lti_start_assessment.

    # We remove the end_assessment_return session data, since the learner has completed the proctoring flow.
    end_assessment_return = request.session.pop('end_assessment_return')
    if end_assessment_return:
            lti_message_hint = 'LtiEndAssessment'
            preflight_url = get_lti_preflight_url(lti_message_hint)

            return redirect(preflight_url)

    return JsonResponse()

def public_keyset(request):
    """
    This is the view that serves as the Assessment Platform's LTI Public Keyset.

    The Proctoring Tool needs to know the Assessment Platform's public keyset URL.
    This information is exchanged out-of-band during the registration phase.
    """
    return JsonResponse(
      get_lti1p3_consumer().get_public_keyset(),
    )

# We do not want Django's CSRF protection enabled for POSTs made by external services to this endpoint.
# This is because Django uses the double-submit cookie method of CSRF protection, but the Proctoring Specification
# lends itself better to the synchronizer token method of CSRF protection.
# Django's method requires an anti-CSRF token to be included in both a cookie and a hidden from value in the request
# to CSRF procted endpoints.
# In the Proctoring Specification, there are a number of issues supporting the double-submit cookie method.
# 1. Django requires that a cookie is sent with the request to the Assessment Platform that contains the anti-CSRF 
#    token. When the learner's browser makes a request to the start_proctoring view, an anti-CSRF token is set in the
#    cookie.
#    The default SameSite attribute for cookies is "Lax" (stored in the Django setting CSRF_COOKIE_SAMESITE),
#    meaning that when the Proctoring Tool redirects the learner's browser back to the Assessment Platform, the browser
#    will not include the previously set cookie in its request to the Assessment Platform. CSRF_COOKIE_SAMESITE can be
#    set to "None", but this means that all third-party cookies will be included by the browser, which may compromise
#    CSRF protection for other endpoints. Note that settings CSRF_COOKIE_SAMESITE to "None" requires that
#    CSRF_COOKIE_SECURE is set to True.
# 2. Django validates a request by comparing the above anti-CSRF token in the cookie to the anti-CSRF token in the POST
#    request parameters. Django expects the anti-CSRF token to be in the POST request parameters with the name
#    "csrfmiddlewaretoken". However, the Proctoring Specification requires that the anti-CSRF token be included in the
#    JWT token with the name "session_data". The Proctoring Tool will not direct the browser to send this anti-CSRF
#    token back with the name "csrfmiddlewaretoken", as it's not part of the Proctoring Services Specification.
# This is why we use the csrf_exempt decorator. It exempts this view from CSRF protection for POST requests.
# TODO: From the Django documentation, "This should not be done for POST forms that target external URLs,
#       since that would cause the CSRF token to be leaked, leading to a vulnerability."
#       What does this mean for this endpoint? Is it unsafe to include the CSRF token in the JWT?
@csrf_exempt
# Per the Proctoring Services specification, the Proctoring Tool can direct the learner's browser to make either a GET
# or POST request to this endpoint.
@require_http_methods(['GET', 'POST'])
def authenticate(request):
    """
    This view is the first step of the OpenID Connect authentication flow. This view may be called the "OIDC
    Authorization end-point."

    The Proctoring Tool responds to the browser's request to Tool's OIDC login initiation URL by directing the learner's
    browser. to make a request against this endpoint. This starts the authentication flow.

    The Assessment Platform directs the learner's browser to make a request to the Proctoring Tool, acting as the
    "authentication response". This request must be made to the URL specified by the "redirect_uri" claim in the
    request.
    
    This signifies the second leg of the LTI launch workflow - otherwise know as the LTI launch or "OpenID Connect
    authorization flow".

    It receives, as a request, the response to the Assessment Platform's request to the Proctoring Tool's OIDC login
    initiation URL and creates a LTI launch request to the Proctoring Tool.

    The Assessment Platform needs to know the Proctoring Tool's OIDC login initiation URL.
    This information is exchanged out-of-band during the registration phase.
    """
    lti_consumer = get_lti1p3_consumer()

    # "The Assessment Platform MUST also include some session-specific data (session_data) that is
    # opaque to the Proctoring Tool in the Start Proctoring message.
    # This will be returned in the Start Assessment message and acts as an anti-CSRF token,
    # the Assessment Tool MUST verify that this data matches the expected browser session
    # before actually starting the assessment."
    # See 3.3 Transferring the Candidate Back to the Assessment Platform.
    # In the synchronizer token method of CSRF protection, the anti-CSRF token must be stored somehow on the server.
    # Note that this generates an anti-CSRF token PER USER SESSION, not per request. Per request is more secure, but
    # I elected to do is on the session for the POC, because it is simpler.
    session_data = request.session.get('lti_proctoring_session_data')
    if session_data is None:
        session_data = get_random_string(32)
        request.session['lti_proctoring_session_data'] = session_data

    start_assessment_url = urljoin(settings.ROOT_URL, reverse('lti:start-assessment'))

    # TODO: The resource link should uniquely represent the assessment in the Assessment Platform.
    # TODO: We SHOULD provide a value for the title attribute.
    # TODO: It's RECOMMENDED to provide a value for the description attribute.
    # TODO: The xblock-lti-consumer library does not currently support setting these attributes.
    resource_link = get_resource_link()

    lti_consumer.enable_proctoring(
        # NOTE TO SELF: attempt_number is an auto-incrementing integer from 1 per learner, per assessment.
        29, # attempt_number
        session_data,
        resource_link,
        start_assessment_url=start_assessment_url,
    )

    # This is necessary for testing with the IMS tool, since the user will be an AnonymousUser without an id.
    # TODO: Replace this with the authenticated user's id.
    # TODO: Remove this once testing is complete.
    user_id = 1 if request.user.id is None else request.user.id

    # Required user claim data
    lti_consumer.set_user_data(
        #   user_id=request.user.id,
        user_id=user_id,
        # Pass Django user role to library
        role='student'
    )

    # These claims are optional.
    # TODO: This will need to have additional consideration for PII.
    optional_user_identity_claims = get_optional_user_identity_claims()
    lti_consumer.set_proctoring_user_data(
        **optional_user_identity_claims
    )

    context = {}

    # Authorization Servers MUST support the use of the HTTP GET and POST methods defined in RFC 2616 [RFC2616]
    # at the Authorization Endpoint.
    # See 3.1.2.1.Authentication Request of the OIDC specification.
    # https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
    preflight_response_method = request.method
    preflight_response = request.GET if preflight_response_method == 'GET' else request.POST

    context.update({
    'preflight_response': preflight_response.dict(),
    'launch_request': lti_consumer.generate_launch_request(
        preflight_response,
        resource_link,
    )
    })

    # This template renders an auto-submitting form, which makes a POST request to the redirect_uri, specified in the
    # Tool's response to the request the Assessment Platform made to the Tool's OIDC login initiation URL.
    return render(request, 'lti/lti_launch_request_form.html', context)

# We do not want Django's CSRF protection enabled for POSTs made by external services to this endpoint.
# Please see the comment for the authenticate view for a more detailed justification.
@csrf_exempt
# Per the Proctoring Services specification, the Tool can direct the learner's browser to make only a POST request to
# this endpoint.
@require_http_methods(['POST'])
def start_assessment(request):
    """
    This view handles the Proctoring Tool's message to start the assessment, which is a "Tool-Originating Message".

    Once the Proctoring Tool determines the user is ready to start the proctored assessment (e.g. their environment
    has been secured and they have completed user identity verification), it send the Assessment Platform an LTI
    message. Because it is a "Tool-Originating Message" and no user identity is shared, the message is a signed JWT, not
    an ID Token.

    The Proctoring Tool needs to know the location of this endpoint on the Assessment Platform's; this endpoint is
    referred to as the "start assessment URL. This information is sent to the Proctoring Tool in the
    Assessment Platform's response to the Tool's request to the login endpoint. It is included
    as the required claim "start_assessment_url" in the ID Token.
    """
    # TODO: Here we'd do all the start of assessment things.

    lti_consumer = get_lti1p3_consumer()

    # Let's grab the session_data stored in the learner's session. This will need to be compared
    # against the session_data claim in the proctoring token included by the Tool in the request.
    # TODO: The use of the user session to store the CSRF token on the server
    #       does not work without changing the value of the SESSION_COOKIE_SAMESITE Django setting to
    #       'None', which allows the browser to send the session cookie as a third-party cookie. What
    #       security considerations are there?
    session_data = request.session.get('lti_proctoring_session_data')

    start_assessment_url = urljoin(settings.ROOT_URL, reverse('lti:start-assessment'))
    
    # TODO: The resource link should uniquely represent the assessment in the Assessment Platform.
    # TODO: We SHOULD provide a value for the title attribute.
    # TODO: It's RECOMMENDED to provide a value for the description attribute.
    # TODO: The xblock-lti-consumer library does not currently support setting these attributes.
    resource_link = get_resource_link()

    lti_consumer.enable_proctoring(
        # NOTE TO SELF: attempt_number is an auto-incrementing integer from 1 per learner, per assessment.
        29, # attempt_number,
        session_data,
        resource_link,
        start_assessment_url=start_assessment_url,
    )

    # This is necessary for testing with the IMS tool, since the user will be an AnonymousUser without an id.
    # TODO: Replace this with the authenticated user's id.
    # TODO: Remove this once testing is complete.
    user_id = 1 if request.user.id is None else request.user.id

    # Required user claim data
    lti_consumer.set_user_data(
    user_id=user_id,
      # Pass Django user role to library
      # TODO: A role of 'student' is not correctly mapped to the corresponding LTI claim for the Proctoring
      #       Specification.
      role='student'
    )
    
    # These claims are optional. They are necessary to set in order to properly verify the verified_user claim,
    # if the Proctoring Tool includes it in the JWT.
    # TODO: This will need to have additional consideration for PII.
    optional_user_identity_claims = get_optional_user_identity_claims()
    lti_consumer.set_proctoring_user_data(
        **optional_user_identity_claims
    )

    try:
        lti_response = lti_consumer.check_and_decode_proctoring_token(request.POST.get('JWT'))
    except (MalformedJwtToken, TokenSignatureExpired):
        return JsonResponse(
            {'error': 'invalid_grant'},
            status=400,
        )
    except NoSuitableKeys:
        return JsonResponse(
            {'error': 'invalid_client'},
            status=400
        )
    except (BadJwtSignature, InvalidClaimValue, MissingRequiredClaim):
        # TODO: I'm not sure whether this is the right OIDC error ID.
        return JsonResponse(
            {'error': 'invalid_token'},
            status=400
        )
    except UnauthorizedToken:
        return JsonResponse(
            {'error': 'invalid_token'},
            status=403
        )

    response = JsonResponse(lti_response)

    # If the Proctoring Tool specifies the end_assessment_return claim in its LTI launch request,
    # the Assessment Platform MUST send an End Assessment Message at the end of the learner's
    # proctored exam.
    # See 4.4 End Assessment Message.
    end_assessment_return = lti_response.get('end_assessment_return')
    if end_assessment_return:
        # TODO: We have to store this value somehow. We could store it in a cookie or in the user's session,
        # for example.
        request.session['end_assessment_return'] = True

    return response
