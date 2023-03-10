Token System for Exam Access
=================================

Status
------

Approved (circa September 2022)

Context
-------
Exam integrity and security is a fundamental element of special exams on the edX platform, which includes
timed exams, practice proctored exams, onboarding exams, and proctored exams. In order to ensure exam
integrity and security, edX learners should only be able to see special exam content when they are authorized to do so.

In the legacy experience for exams, ``edx-proctoring``, exam access was gated by frontend interstitials, as well as a
check on the backend before rendering the student view. The access check on the backend was possible because the LMS
directly imports ``edx-proctoring``, and has access to specific functions that return whether or not the content
should be visible to a learner in an exam. More details on the legacy experience can be found in the `original discovery
doc <https://2u-internal.atlassian.net/wiki/spaces/PT/pages/15440845/MST-1210+How+do+we+do+access+control+for+exam+content+without+edx-proctoring>`_.

In the new experience, which uses the ``edx-exams`` IDA as a backend, the LMS cannot directly import any functionality from
``edx-exams``, as it is an IDA. Therefore, while the frontend gating still exists via the same interstitials from the legacy
experience, there is no way to gate access to exam content on the backend, meaning that the content could be
directly accessed via URL.

With the new experience using ``edx-exams`` as a backend, we need a way to maintain access control.

Decision
--------
A JWT token will be used to determine if a user has access to view an x-block. ``edx-platform`` will not make any direct
calls to the ``edx-exams`` service to determine if a user has access to view the content of an exam.

Consequences
------------
#. A new repository, ``token-utils`` will be created to contain all logic related to access gating via JWT token.

    * ``token-utils`` is a plug-in that will be used by both the LMS and by the ``edx-exams`` service.

#. The learning MFE will make a call to fetch an access token prior to rendering any content.

    * The access token will be valid for a specific user, exam, and time

    * Once the access token is retrieved, it will be appended as a query parameter to the URL that is called to
      render x-block content.

#. The x-block being rendered will be responsible to check that the access token is valid.

    * The x-block will unpack the access token that has been added as a query parameter, and use
      `token-utils` to determine if the access token is valid.

References
----------

* Discovery Doc for Exam Access: https://2u-internal.atlassian.net/wiki/spaces/PT/pages/15440845/MST-1210+How+do+we+do+access+control+for+exam+content+without+edx-proctoring
* Discovery Doc for JWT Token Access: https://2u-internal.atlassian.net/wiki/spaces/PT/pages/36110391/Ticket+JWT+Token+for+Exam+Access+Control
* ``token-utils`` Repository: https://github.com/edx/token-utils
