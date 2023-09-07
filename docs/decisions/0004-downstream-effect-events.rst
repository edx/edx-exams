Implementation of Event Driven Architecture for Exam Downstream Effects
=======================================================================

Status
------

Draft (circa Sept 2023)

Context
-------
We are porting any downstream effects of exam submission and review from the legacy exams system, edx-proctoring, to edx-exams.
Most of these downstream effects will reflect calls that edx-proctoring (which is a plugin) makes to various edx-platform services,
such as grades, credits, and certificates.

Decision
--------
We decided to use the event bus to send info to edx-platform services without needing a response as one would in a REST framework.

We are porting the downstream effects of exam submission and review because they are both essential and easy to translate into events:

  * Grades Override - A call to the grades service to override a grade when an exam attempt is rejected.

  * Undo Grades Override - A call to the grades to undo such an override when marking a rejected attempt as verified.

  * Instructor Delete Attempt - A call to the instructor service to delete an exam attempt.

  * Instructor Complete Attempt - A call to the instructor service that marks the exam as completed.

  * Instructor Is Course Staff - A call to the instructor service to check if a user is course staff.

  * Invalidate Certificate - A call to the certificates service to invalidate a leaner’s edx certificate for a course.

  * Set Credit Requirement Status - A call to the credits service to create or modify a learner’s credit requirement status for an exam.

The following are not being ported/implemented as part of this decision:

  * Credit Prerequisite Check:

    * In edx-proctoring, we call the credits service to see if a learner has completed the prerequisites for an exam.

    * Translating this into edx-exams would require a request-response call to be made from edx-exams to edx-platform. This would create an undesired circular dependency,as we already have edx-platform making such calls to edx-exams.

    * Instead, we have decided to implement an endpoint in the credits service that returns the prereq status, which will be called directly from the exams UI.

  * Name Affirmation:

    * Currently, edx-proctoring calls the name affirmation service in order to match the name that Proctortrack sees on the learner’s ID to the user’s verified name in the LMS database.

    * We do not plan to implement this since it is very likely that 2U will not require the matching of one’s verified name in edx-platform to the names on their IDs in the future.

  * Enrollments:

    * This is only called to get a learner’s onboarding status.

Here are all of the service calls in edx-proctoring that we’d want re-created in edx-exams, translated into events:
 ====================================== ================================================================================================ =========================================================================================== ============================================ =============================================== ========================================================================= ====================================================================================== 
  Event Type                             Production Context                                                                               Data sent                                                                                   Consumer Location                            Functions Called                                General Context for Calls                                                 Expected Result                                                                       
 ====================================== ================================================================================================ =========================================================================================== ============================================ =============================================== ========================================================================= ====================================================================================== 
  Grades Override                        When an exam attempt is rejected.                                                                user_id, course_key_or_id, usage_key_or_id, earned_all, earned_graded, overrider, comment   lms/djangoapps/grades/signals.py             override_subsection_grade in api.py             When we need to override a grade from any service.                        A grade override object is created or modified in the grades service within the LMS.  
  Undo Grades Override                   When an exam attempt is verified after previously being rejected, OR when it is deleted/reset.   user_id, course_key_or_id, usage_key_or_id                                                  lms/djangoapps/grades/signals.py             undo_override_subsection_grade in services.py   When we need to undo a grade override from any service.                   A grade override object is deleted in the grades service within the LMS.              
  Instructor Reset Subsection            When an exam attempt is deleted/reset.                                                           username, course_id, content_id, requesting_user                                            lms/djangoapps/instructor/signals.py         reset_student_attempts in enrollments.py        When we need to reset a student’s state in a subsection.                  A learner's state for a subsection is reset.                                          
  Instructor Mark Subsection Completed   When an exam attempt is completed.                                                               username, content_id                                                                        lms/djangoapps/instructor/signals.py         update_exam_completion_task in tasks.py         When we need to mark a subsection as completed.                           A subsection is marked completed for a learner.                                       
  Invalidate Certificate                 When an exam attempt is rejected.                                                                user_id, course_key_or_id                                                                   lms/djangoapps/certificates/signals.py       invalidate_certificate in services.py           When we need to invalidate a learner's certificate.                       A certificate object's status is set to "unavailable".                                
  Set Credit Requirement Status          When exam attempt is completed.                                                                  user_id, course_key_or_id, req_namespace, req_name, status                                  openedx/core/djangoapps/credits/signals.py   set_credit_requirement_status in services.py    When we need to create or modify a learner's credit requirement status.   A credit requirement status object is created or modified within the LMS.             
 ====================================== ================================================================================================ =========================================================================================== ============================================ =============================================== ========================================================================= ====================================================================================== 

Consequences
------------
#. Event definitions implemented in openedx-events

  * Defining the events and the data sent in each in this abstraction layer is fundamental to making event bus work.

  * We have designed these events to be "generic", such that they can be triggered under contexts outside of exams by other services.

#. Event producers implemented in edx-exams

  * We will implement these producers in the backend in the places we want these events to be triggered.

#. Event consumers added to edx-platform

  * We will add consumers in the signals.py file in each edx-platform service's respective folders.

  * These consumers will call other service or api functions in those folders.

#. Using event driven architecutre circumvents circular dependencies

  * This prevents edx-exams and edx-platform from going back and forth to ask each other for information.

References
----------

* Discovery Doc for M6: https://2u-internal.atlassian.net/wiki/spaces/PT/pages/539066520/MST-1789+M6+Exam+Review+and+Downstream+Triggers+Scope+Definition+and+Story+Writing#Implementation:
* How to use the event bus: https://openedx.atlassian.net/wiki/spaces/AC/pages/3508699151/How+to+start+using+the+Event+Bus#Resources
* ``openedx-events`` repository: https://github.com/openedx/openedx-events/blob/main/openedx_events/learning/signals.py