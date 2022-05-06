edx-exams LTI for Proctoring Proof-of-Concept
=============================================

This Djangoapp is an implementation of a proof-of-concept of an LTI launch for proctoring using the `IMS Proctoring
Services Specification`_.

.. _IMS Proctoring Services Specification: http://www.imsglobal.org/spec/proctoring/v1p0

Overview
--------

Please note that the code in this Djangoapp is part of a proof-of-concept and has been approved and merged as a
reference for future work. Changes will be necessary before this code is ready for production. For example, most of
the view logic in this Djangoapp will need to move to the xblock-lti-consumer library once that library has been
refactored to be less reliant on xBlocks and the xBlock runtime. For that reason, some of this code may not be
appropriate for a production environment without further modification.

Also note that this Djangoapp relies on changes to the xblock-lti-consumer library that are in a branch and not on the
master branch.
