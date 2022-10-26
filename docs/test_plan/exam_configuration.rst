Exam Setup and Configuration
============================

Exam Configuration (edx-exams)
------------------------------

Prerequisite Steps:
   #. Make sure `course_apps.exams_ida` CourseWaffleFlag is enabled for your test course
   #. An LTI proctoring provider should be chosen for the course
   #. Log in as a user with course staff permissions for your test course
   #. Navigate to the course in studio

Create a timed exam
^^^^^^^^^^^^^^^^^^^
#. Create a new subsection with a single unit
#. Click the gear on the subsection and set the exam type to timed with an allotted time of 00:30
#. Publish the section
#. Using edx-exams django admin or a database connection

   #. Ensure and exam exists for the course id and content id of the created subsection
   #. The exam type should be timed with a time limit of 30mins

Create a proctored exam
^^^^^^^^^^^^^^^^^^^^^^^
#. Create a new subsection with a single unit
#. Click the gear on the subsection and set the exam type to proctored with an allotted time of 00:30
#. Publish the section
#. Using edx-exam django admin or a database connection

   #. Ensure an exam exists for the course id and content id of the created subsection
   #. The exam type should be proctored with a time limit of 30mins

Update a published exam
^^^^^^^^^^^^^^^^^^^^^^^
#. Find an existing timed or proctored subsection
#. Click the gear on the subsection and change the allotted time and due date
#. Save
#. Using edx-exam django admin or a database connection

   #. Ensure the exam for that subsection's time limit and due date have been updated

Disable a published exam
^^^^^^^^^^^^^^^^^^^^^^^^
#. Find an existing timed or proctored subsection
#. Click the gear on the subsection and change the exam type to 'None'
#. Save
#. Using edx-exam django admin or a database connection

   #. Ensure the exam for that subsection is not active

Update a proctored exam to be timed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Find an existing proctored subsection or create a new one
#. Click the gear on the subsection and change the exam type to 'Timed'
#. Save
#. Using edx-exam django admin or a database connection

   #. There should be two exams for this subsection
   #. The timed exam should be active
   #. The proctored exam should not be active

Remove an exam
^^^^^^^^^^^^^^
#. Find an existing timed or proctored subsection
#. Delete the entire subsection and publish
#. Using edx-exam django admin or a database connection

   #. Ensure the exam for that subsection is not active

Exam Configuration with Legacy Provider (edx-proctoring)
--------------------------------------------------------

Prerequisite Steps:
   #. A legacy (edx-proctoring) proctoring provider should be chosen for the course (course-v1:edX+cheating101+2018T3 would work)
   #. Enable the :code:`course_apps.exams_ida` CourseWaffleFlag for your test course
   #. Log in as a user with course staff permissions
   #. Navigate to the course in studio

Create a proctored exam
^^^^^^^^^^^^^^^^^^^^^^^
#. Create a new subsection with a single unit
#. Click the gear on the subsection and set the exam type to proctored with an allotted time of 00:30
#. Publish the section
#. Using LMS django admin or a database connection
    #. Ensure an exam exists for the course id and content id of the configured section
    #. The exam should be proctored and have a time limit of 30 minutes

Update a proctored exam
^^^^^^^^^^^^^^^^^^^^^^^
#. Find or create a proctored exam subsection
#. Click the gear on the subsection and change the allotted time and due date
#. Publish the section
#. Using LMS django admin or a database connection
    #. Ensure an exam exists for the course id and content id of the configured section
    #. The exam should be be updated with the correct time limit and due date

Remove an exam
^^^^^^^^^^^^^^
#. Find or create a timed or proctored subsection that is safe to delete
#. Delete the entire subsection and publish
#. Using LMS django admin or a database connection

   #. Ensure the exam for that subsection is not active

Proctoring Provider Configuration
---------------------------------

Prerequisite Steps:
   #. Using edx-exams django admin make sure there is at least one proctoring provider available
   #. Make sure :code:`course_apps.exams_ida` waffle is enabled for your test course

Course staff cannot change proctoring provider after course start date
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Login as a course staff (non edX admin) user
#. Navigate to a course in studio and set its start date to a future date
#. Go to the 'Proctored Exams Settings' page from the settings dropdown
#. Ensure the proctoring provider cannot be changed

edX staff can change proctoring provider after course start date
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Login as an edX admin user
#. Navigate to a course in studio and set its start date to a future date
#. Go to the 'Proctored Exams Settings' page from the settings dropdown
#. Ensure the proctoring provider can be changed

If exam IDA waffle is enabled, both LTI and legacy proctoring providers are available
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Go to the 'Proctored Exams Settings' page from the settings dropdown in Studio
#. Proctoring providers configured in the LMS should be available options along with providers in edx-exams

If exam IDA waffle is not enabled, only legacy proctoring providers are available
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Temporarily update :code:`course_apps.exams_ida` waffle to NOT be enabled for your test course
#. Go to the 'Proctored Exams Settings' page from the settings dropdown in Studio
#. Only proctoring providers configured in the LMS should be displayed, providers in edx-exams are not shown

Select legacy proctoring provider
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Go to the 'Proctored Exams Settings' page from the settings dropdown in Studio
#. Select any non LTI provider (Proctortrack, SoftwareSecure, etc) and save
#. Reload the page, the new setting should persist
#. Validate the courses proctoring provider in the CMS has been updated to match your selection

   #. https://studio.stage.edx.org/api/contentstore/v1/proctored_exam_settings/<COURSE_ID> can be used to check this value

Select LTI proctoring provider
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Go to the 'Proctored Exams Settings' page from the settings dropdown in Studio
#. Select an LTI provider from those configured in edx-exams and save
#. Reload the page, the new setting should persist
#. Validate the courses proctoring provider in the CMS has been updated to 'lti_external'
   
   #. https://studio.stage.edx.org/api/contentstore/v1/proctored_exam_settings/<COURSE_ID> can be used to check this value

#. Using edx-exams django admin find the CourtsExamConfiguration for the test course and validate the provider matches your selection

Update configured LTI provider back to a legacy option
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Go to the 'Proctored Exams Settings' page from the settings dropdown in Studio
#. Make sure an LTI provider is already selected for the course
#. Select any non LTI provider (Proctortrack, SoftwareSecure, etc) and save
#. Reload the page, the new setting should persist
#. Validate the courses proctoring provider in the CMS has been updated to match your selection

   #. https://studio.stage.edx.org/api/contentstore/v1/proctored_exam_settings/<COURSE_ID> can be used to check this value

#. Using edx-exams django admin find the CourseExamConfiguration for the test course and validate the provider is set to 'None'

Update LTI provider with existing exams
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Go to the 'Proctored Exams Settings' page from the settings dropdown in Studio
#. Make sure an LTI provider is already selected for the course
#. Create a new proctored exam section in Studio and publish
#. Go to the 'Proctored Exams Settings' page and select a different LTI provider
#. Using edx-exams django admin or a database connection find Exams for the test course

   #. There should be an exam object for the originally selected provider this exams must NOT be active 
   #. There should be an exam object for the newly selected provider this exams must be active 

Update LTI provider to legacy option with existing exams
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Go to the 'Proctored Exams Settings' page from the settings dropdown in Studio
#. Make sure an LTI provider is already selected for the course
#. Create a new proctored exam section in Studio and publish
#. Go to the 'Proctored Exams Settings' page and select any non LTI provider (Proctortrack, SoftwareSecure, etc)
#. Using edx-exams django admin or a database connection find Exams for the test course

   #. There should be an exam object for the originally selected provider this exams must NOT be active 
   #. Find the CourseExamConfiguration for the test course and validate the provider is set to 'None'
