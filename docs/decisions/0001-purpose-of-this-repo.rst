1. Purpose of this Repo
=======================

Status
------

Accepted

Context
-------

In April 2022 we `proposed creating a new special exams service
<https://github.com/openedx/edx-proctoring/blob/c5592b2ff2fd95e990d0b9b438228b741a42dbd3/docs/decisions/0004-exam-ida.rst>`_
to replace the existing in-platform plugin. That proposal also includes the following details:

* This IDA will function in parallel with the current edx-proctoring library. edx-platform may use either service for a course.

    * Exams should be considered a periphery service. As such, edx-platform should not depend on this service.

* Changes in exam state that would impact other systems such as grades, completion, credit, or certificates should be pushed to those systems via REST endpoints or using events.

* Data about course content or exam configuration will be pushed to this IDA's REST API as part of the studio publish action. We should replicate data instead of reading directly from the CMS or LMS in an ad-hoc manner.

* This IDA will implement a REST API to expose exam and attempt state information to https://github.com/edx/frontend-lib-special-exams.

* This IDA will not include custom APIs or data calls specific to a single proctoring tool.

References
----------

* Spec Document: https://openedx.atlassian.net/wiki/spaces/PT/pages/3251535873/Independently+Deployable+Special+Exam+Service
