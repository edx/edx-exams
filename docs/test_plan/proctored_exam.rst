Proctored Exams
===============

Helpful ReadTheDocs Pages:

- `Configuring a Proctoring Provider <https://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/proctored_exams/proctored_enabling.html#configuring-proctoring-provider>`_
- `Creating a Proctored Exam <https://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/proctored_exams/pt_create.html#creating-a-proctored-exam>`_

Prerequisite steps:
    #. Use Google Chrome.
    #. Have a staff account.
    #. Have a non-staff learner account enrolled in the verified track for this course.
    #. As your non-staff user in your current window, and enroll in the course where you have set up your proctored exam
    #. In an incognito window, login to your staff account and visit your Support Tools page and search in the email for your non-staff user. You should now see the option to change the enrollment track of that user. Change the enrollment track of the user to ""verified"" (choose any reason when prompted, it doesn't matter).
    #. In that same incognito, still signed in as staff, navigate to the Instructor dashboard.
    #. Find or create a test course within Stage with proctoring enabled and an LTI proctoring provider "Proctorio" chosen, and where the exams IDA waffle flag is enabled.
      #. The exams IDA waffle flag can be found/created in the LMS' Django Admin under "Waffle Flag Course Overrides"
      #. If needed, you can make a new entry using "course_apps.exams_ida" as the waffle flag, the course ID, and by setting it to "Enabled".
    #. Find or create two exam subsections with a type of 'Proctored exam' in your test course.
      #. This can be done by creating a subsection and clicking the 'Configure' button (should look like a gear), going to the "Advanced Tab", and selecting "Proctored"
      #. NOTE: You MUST also set this subsection to be Graded as a Midterm or Final exam.
    #. You should also have a tab open with your event bus logs.

Proctored Exam Flow
-------------------
Expected Behavior: "A paid track learner is able to start, complete, and submit a proctored exam w/ Proctorio via LTI Launch."

Without Proctorio
=================
#. Enter a Proctored Exam. You should see an interstitial stating that "This exam is proctored" with a button that says "Continue to Proctored Exam"
#. Clicking "Continue to Proctored Exam" should bring you to an interstitial titled "Set up and start your proctored exam." with "Start System Check" and "Start Exam" buttons
#. Clicking the "Start Exam" button should pop up a modal that says "Cannot Start Exam"
#. Clicking "OK" closes that modal
#. Clicking "Start System Check" redirects you to https://getproctorio.com/
#. Navigating back one page and clicking "Start Exam" still blocks you from starting the exam

With Proctorio
==============
#. Install the Proctorio extension at https://getproctorio.com/
#. Go through the opening interstitials and click "Start System Check". You should briefly see an lti launch URL containing "/lti_consumer/" in the URL bar, and then be redirected to the Proctorio Instructions page.
#. Immediately navigating back and trying to click "Start Exam" still doesn't allow you to start the exam.
#. Navigating back to the Proctorio Instructions and refreshing on that page causes no issues
#. Go through the Proctorio Setup for your Webcam, Desktop, etc. Upon setup completion, your webcam should appear to the right of the screen along with some controls. You should land on a page that says "Sending you back to your exam." with a link to "Return to Exam". Clicking this link should send you to another interstitial. (NOTE: Clicking this link is time-bound so make sure to click it fast)
#. Clicking "Return to Exam" directs you to a page titled "Important" w/ another header saying "Proctored Exam Rules", and a "Start Exam" Button
#. Clicking "Start Exam" directs you to the exam.
#. Clicking "End My Exam" directs you to a "Are you sure you want to end your proctored exam?" Interstitial
#. Clicking "No I'd like to continue working" sends you back to the exam.
#. Clicking "Yes end my proctored exam" ends the exam and directs you to a "You have submitted this proctored exam for review" page
#. In the course view, the exam you took is marked as completed (with a green checkmark)
#. In a separate exam, go through the setup again and, but instead of clicking on "Return to exam" on the "Sending you back to your exam" page, simply wait, You should be sent to the "Important"/"Start Exam" interstitial automatically.
#. In this separate exam, start the exam, then open devtools using Cmd+Option+I on Mac (F12 on Windows). This should error out the exam and load a "Error with proctored exam" page AND open the "Proctorio Support" page in another tab


Exams Dashboard
---------------
Expected Behavior: ACS Endpoint calls work, able to review/reset exam attempts

Dashboard UI
============
#. Clicking on the "Special Exams" tab loads the *new* version of the exams dashboard.
#. Clicking on the "Review Dashboard" tab within the exams dashboard should open a new tab to the Proctorio Dashboard for instructors.
#. Clicking the "Select An Exam" dropdown shows the list of exams for the course.
#. Filtering by exam name in the exam selection dropdown brings up the expected exams (e.g. querying "M4-M6" shows all the exams in that section)
#. Selecting a specific exam (i.e. the ones you just took) loads the respective exam attempts for those exams
#. The exam attempts are in the expected status, e.g. successful attempts are submitted or verified, and the errored attempts are errored.
#. Filtering by username only shows exam attempts for that username.
#. The status changes for these exam attempts look the same in the edx-exams admin

Resetting an exam attempt
=========================
#. Clicking "Reset" on an exam attempt brings up a confirmation modal.
#. Clicking "No (Cancel)" closes the modal and nothing changes
#. Clicking "Yes I'm Sure" removes the exam attempt from the table (effectively confirming that it's been reset)
#. The exam attempt no longer appears in the edx-exams admin

Reviewing Verified/Rejected Attempts
====================================
#. Exam attempts with a status of "Verified" have a button/link at the end of their rows titled "Manual Review"
#. A modal pops up upon clicking "Manual Review" that contains "Cancel" and "Reject" Buttons
#. Clicking "Cancel" closes the modal.
#. Clicking "Reject" changes the attempt status to "rejected" both in the UI and in the edx-exams admin
#. The same exam attempts with a status of "Rejected" have a button at the end of their rows saying "Manual Review"
#. A modal pops up upon clickin "Manual Review" that only has the "Cancel" and "Verify" Buttons
#. Clicking "Cancel" closes the modal.
#. Clicking "Verify" changes the attempt status to "verified" both in the UI and in the edx-exams admin

Reviewing "Errored" attempts
============================
Instructions: Create a couple of errored attempts by opening Chrome DevTools during an exam.
#. Clicking the "Review Required" button pops up a modal that says "Update review status"
#. Clicking "Cancel" closes modal
#. Clicking "Verify" marks attempt as verified both in the dashboard and in the edx-exams admin
#. Clicking "Reject" marks attempt as reject both in the dashboard and in the edx-exams admin

Reviewing "Second Review Required" attempts
===========================================
Instructions: Go into another exam and be suspiscious. Block your webcam, leave for a few seconds, make strange noises, open a bunch of tabs, watch some youtube, open wikipedia, ask chatgpt for the answer to life, etc. Note you will need to do this a couple of times.
#. Submit your suspiscious exam attempt, and check the exams dashboard. Assuming you were suspiscious enough, you should see a row that has a status of "Second Review Required" AND has a "Review Required" button for your attempt.
#. Clicking the "Review Required" button spawns a modal that says "Update review status"
#. Clicking "Cancel" closes modal
#. Clicking "Verify" marks attempt as verified both in the dashboard and in the edx-exams admin
#. Clicking "Reject" marks attempt as reject both in the dashboard and in the edx-exams admin
#. Clicking the "Review Dashboard" link in the modal "loads" the review dashboard (NOTE: This shouldn't work yet, and will load a broken page instead)


Event Bus
---------
Expected Behavior: Events are produced and consumed by the correct services as expected.

Instructions: Open the UI to track event bus logs related to exam attempts to check that downstream effect related events were consumed/produced as expected.
#. On exam attempt submission, the 'org.openedx.learning.exam.attempt.submitted.v1' event is produced and consumed as such:
  #. Produced by edx-exams
  #. Consumed by the Instructor service
  #. Consumed by the Credits service
#. On exam attempt being verified, the 'org.openedx.learning.exam.attempt.verified.v1' event is produced and consumed as such:
  #. Produced by edx-exams
  #. Consumed by the Grades service
  #. Consumed by the Certificates service
  #. Consumed by the Credits service
#. On exam attempt being rejected, the 'org.openedx.learning.exam.attempt.rejected.v1' event is produced and consumed as such:
  #. Produced by edx-exams
  #. Consumed by the Grades service
  #. Consumed by the Credits service
#. On exam attempt erroring out, the 'org.openedx.learning.exam.attempt.errored.v1' event is produced and consumed as such:
  #. Produced by edx-exams
  #. Consumed by the Credits service
#. On exam attempt reset, the 'org.openedx.learning.exam.attempt.reset.v1' event is produced and consumed as such:
  #. Produced by edx-exams
  #. Consumed by the Instructor service
  #. Consumed by the Credits service
