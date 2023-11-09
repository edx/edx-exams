Timed Exams
===========

Helpful ReadTheDocs Pages:

- `Configuring a Proctoring Provider <https://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/proctored_exams/proctored_enabling.html#configuring-proctoring-provider>`_
- `Creating a Proctored Exam <https://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/proctored_exams/pt_create.html#creating-a-proctored-exam>`_

Prerequisite steps:
    #. Find or create a test course with proctoring enabled and an LTI proctoring provider chosen
    #. Find or create a test course without an LTI proctoring provider chosen
    #. Find or create an exam section with a type of 'timed exam' in each course
        #. This can be done by creating a subsection and clicking the 'Configure' button (should look like a gear), going to the "Advanced Tab", and selecting "Timed"
    #. Have a non-staff learner account enrolled in the verified track for both courses

Timed Exam Access
-----------------
Ensure the following scenarios pass for both test courses.

A paid track learner is able to start, view, and submit a timed exam
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #. Log in as a verified learner and navigate to the exam section
    #. You should see an interstitial with the following information:
        #. Statement that this is a timed exam
        #. The number of minutes allowed to complete the exam. This should match the `time allotted` value in studio.
        #. A button or link to start the exam
    #. Click the link to start the exam
    #. You should see the first unit in the exam
    #. The exam timer is shown. (tested further in the Exam Timer section below)
    #. Click end my exam using the timer banner
    #. You should see an interstitial confirming if you want to submit
    #. Submit the exam
    #. You should see an interstitial confirming the exam has been submitted
    #. If you navigate away and return to this section you should still see the submitted interstitial

A paid track learner is not able to enter an expired exam (Instuctor paced courses only)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #. In studio, set the due date for the exam in the past
    #. Log in as a verified learner and navigate to the timed exam section
    #. An interstitial is shown stating that the due date for this exam has passed

A paid track learner is not able to view exam content outside of the exam
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #. Log in as a staff user and navigate to the exam section
    #. View the first unit in the exam
    #. Using devtools, find and copy the iframe url for the current unit
    #. Logout and log back in as a verified learner
    #. Open the copied url in a browser tab, keep this window open
    #. The unit should not render
    #. Navigate to the exam section and start the exam
    #. Refresh your window containing the unit iframe url
    #. The unit should render
    #. Submit the exam and wait at least 2 minutes
    #. Refresh your window containing the unit iframe url
    #. The unit should not render

Exam Timer
----------
Ensure the following scenarios pass for both test courses.

Exam timer functions during a timed exam
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #. Log in as a verified learner and begin a timed exam
    #. When viewing exam content there should be a banner with the following information:
        #. Notification you that you are in a timed exam
        #. A button to end the exam
        #. A timer counting down from the correct `time allotted` for this exam
    #. The timer should return with the correct value (meaning it continues to count down on the backend) when you:
        #. Refresh the page 
        #. Navigate to other course content
    #. Click end my exam on the banner
    #. You should see an interstitial confirming if you want to submit
        #. The timer should continue to count down
    #. Click I want to continue working
    #. You should be returned to the exam content
    #. Click end my exam on the banner
    #. Click submit on the confirmation page
    #. You should see an interstitial confirming the exam has been submitted

If the exam timer reaches zero the exam is automatically submitted
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #. (optional) In studio, set `time allotted` on the timed exam to 2-3 minutes to ease testing
    #. Log in as a verified learner and begin the timed exam
    #. Observe the timer as it approaches zero
    #. The timer should visually indicate low time remaining
    #. The timer should pause at 00:00 for approximately 5 seconds
    #. An interstitial is shown notifying the learner their exam time has expired and answers have been automatically submitted.
    #. If you modified `time allotted` please reset it to the initial value

A learner is given limited time if starting a exam that is nearly due
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #. In studio, verify `time allotted` for the exam is greater than 5 minutes
    #. In studio, set the due date for the exam to 5 minutes from now
    #. Log in as a verified learner and navigate to the timed exam section
    #. You should see an interstitial that you have 5 minutes to complete the exam
    #. Begin the exam, the timer should reflect the reduced time limit
