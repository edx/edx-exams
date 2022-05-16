Support for Multiple Exam Systems
=================================

Status
------

Propsed (circa May 2022)

Context
-------
The addition of this service to Open edX will result in two separate services
for managing exams, this IDA and the `edx-proctoring`_ plugin. Because this IDA will
not support existing vendor integrations with the same feature set, edx-proctoring cannot be deprecated
right away. As a result, we need a solution that allows course teams to choose a proctoring tool
that is set up in either service but avoids adding configuration of lots of switching code to edx-platform.

Decision
--------
This service will include all logic necessary to determine which proctoring implementation a particular API
request is relevant for and forward requests `edx-proctoring`_ where appropriate.

#. edx-platform will not have configuration or state indicating if an exam or proctoring provider is configured
   by edx-exams or edx-proctoring.

#. Any request for an API function that exists in this codebase will call the edx-exams REST API only.

    * edx-exams will determine if a request should be forwarded to edx-proctoring or be processed internally.

#. Any request for an API function that does not have an implementation in edx-exams will
   continue to use the edx-proctoring python api.

    * These features should disable gracefully if no configuration is found.


Consesqunces
------------
#. edx-proctoring will have additional REST API endpoints created to handle requests from edx-exams in decision #2 above

#. Both edx-proctoring and edx-platform will have expanded error logic to handle graceful degradation of
   features not included in edx-exams. For example, onboarding exams or creating a review policy.

#. A new django app will be added to this codebase to handle all switching logic and requests to edx-proctoring.

    * This app will be enabled as middleware on API endpoints called by edx systems.

    * When edx-proctoring is no longer in use this middleware and corresponding app should be removed.

#. As features are added to edx-exams existing implementations of that feature will be refactored to integrate
   with this service instead of edx-proctoring.

References
----------

* Discovery Doc: https://2u-internal.atlassian.net/wiki/spaces/PT/pages/15438674/Discovery+Support+multiple+proctoring+subsystems

.. _edx-proctoring: https://github.com/openedx/edx-proctoring
