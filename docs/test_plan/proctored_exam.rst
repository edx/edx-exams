Proctored Exams
===============

Helpful ReadTheDocs Pages
-------------------------
- `Configuring a Proctoring Provider <https://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/proctored_exams/proctored_enabling.html#configuring-proctoring-provider>`_
- `Creating a Proctored Exam <https://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/proctored_exams/pt_create.html#creating-a-proctored-exam>`_


Proctoring Set Up Steps
-----------------------
    - As of November 2023, there is a course available for testing in edX's staging environment at https://learning.stage.edx.org/course/course-v1:edx+PROC100+1T2023/home. You should be able to test using this course so long as you have access to both an instructor and learner account.
    - Otherwise, if you are developing on Open edX locally, then you should follow the instructions below
   
    #. Find or create a test course that has proctoring enabled and an LTI proctoring provider chosen, where a verified track exists, and where the exams IDA waffle flag is enabled
        - The exams IDA waffle flag can be found/created in the LMS' Django Admin under "Waffle Flag Course Overrides"
        - If needed, you can make a new entry using "course_apps.exams_ida" as the waffle flag, the course ID, and by setting it to "Enabled"
    #. Find or create two exam subsections with a type of 'Proctored exam' in your test course
        - This can be done by creating a subsection and clicking the 'Configure' button (should look like a gear), going to the "Advanced Tab", and selecting "Proctored"
        - You MUST also set this subsection to be Graded as a Midterm or Final exam
        - This subsection should contain at least one unit with one gradeable block, e.g. a generic multiple choice question in order to test downstream effects to the gradebook

User Set Up Steps
-----------------
    #. Use Google Chrome as your browser for these tests
    #. In your platform, log in with a non-staff learner account enrolled in the verified track for this course
        - The default credentials for local development are (Username=verified@example.com Password=edx)
    #. As your non-staff user in your current window, and enroll in the course where you have set up your proctored exam
    #. In an incognito window, login into an account with staff or instructor level permissions
        - The default credentials for local development are (Username=edx@example.com Password=edx)
    #. Visit your Support Tools page for managing enrollments. Enter the email for your non-staff user in the search bar. You should now see the option to change the enrollment track of that user. Change the enrollment track of the user to "verified" (choose any reason if prompted, it doesn't matter)
        - Default local URL for changing enrollments is http://localhost:18000/support/enrollment
    #. In that same incognito window, while still signed into your staff or instructor level account, navigate to the exams dashboard
        - This can be found by going to the course view for the course you are testing (the one with all the checkboxes and collapsable course sections), then navigating to the "Instructor" tab to get to the Instructor Dashboard, then navigating to the "Special Exams" tab within the Instructor dashboard.

Proctored Exam Flow
===================
Expected Behavior: "A paid track learner is able to start, complete, and submit a proctored exam using Proctoring Software that is launched via LTI."

Can't Start Exam Without Proctoring Software Installed
------------------------------------------------------
#. Enter a Proctored Exam without proctoring software installed. You should see an interstitial stating that "This exam is proctored" with a button that says "Continue to Proctored Exam"
#. Clicking "Continue to Proctored Exam" should bring you to an interstitial titled "Set up and start your proctored exam." with "Start System Check" and "Start Exam" buttons
#. Clicking the "Start Exam" button should pop up a modal that says "Cannot Start Exam"
#. Clicking "OK" should close that modal
#. Clicking "Start System Check" should redirect you to your proctoring setup page
#. Navigating back one page and clicking "Start Exam" should still block you from starting the exam

Can't Start Exam Without Proctoring Software Running
----------------------------------------------------
#. Install the proctoring software that you've configured with your platform. Go through the opening interstitials and click "Start System Check". This should load your respective Proctoring Software Setup page
#. Immediately navigating back and trying to click "Start Exam" should't allow you to start the exam
#. Navigating back to your proctoring software setup page and refreshing on that page should cause no issues
#. Go through your proctoring software setup for your Webcam, Desktop, etc. Upon setup completion, you should be redirected back to an exam interstitial with just the "Start Exam" button
#. Close your proctoring software and click "Start Exam". The exam should not start

Exam Flow Works With Proctoring Software Installed & Running
------------------------------------------------------------
#. Go through the steps 1-4 in the "Can't Start Exam Without Proctoring Software Running" section again
#. This time without closing your proctoring software, clicking "Start Exam". You should be brought to your exam, with a timer running above the exam questions.
#. Complete whatever question you put inside your exam w/ the correct answer. Clicking "End My Exam" should direct you to a "Are you sure you want to end your proctored exam?" interstitial
#. Clicking "No I'd like to continue working" should send you back to the exam
#. Clicking "Yes end my proctored exam" should end the exam and directs you to a "You have submitted this proctored exam for review" page
#. Clicking "Yes end my proctored exam" should also close your proctoring software automatically.
#. In the course view, the exam you took should be marked as completed (with a green checkmark)

Proctorio-Specific Tests
========================
These tests are for those using Proctorio as their proctoring provider

Exam Flow Works as Expected
---------------------------
#. With Proctorio not installed, clicking "Start System Check" redirects you to https://getproctorio.com/
#. Go through the Proctorio Setup for your Webcam, Desktop, etc. Upon setup completion, your webcam should appear to the right of the screen along with some controls. 
#. On the "Return to exam" page, DO NOT click on the "Sending you back to your exam" page. Wait instead, and you should be sent to the "Important"/"Start Exam" interstitial automatically
#. In a separate exam, go through the setup again and on the "Sending you back to your exam." page, click "Return to Exam". Clicking this link should send you to another interstitial. (NOTE: Clicking this link is time-bound so make sure to click it fast)
#. Clicking the "Return to Exam" button should direct you to a page titled "Important" w/ another header saying "Proctored Exam Rules", and a "Start Exam" Button

Exams Dashboard
===============
Expected Behavior: Calls to the ACS Endpoint work, instructors can review/reset exam attempts, and expected downstream effects (e.g. w/ completion, credits, certificates, etc) of modifying an exam attempt's status occur
NOTE: These instructions currently do not account for downstream effects involving a learner's credit requirement status. We currently have no plan to include these

Dashboard UI Loads Exam Attempts
--------------------------------
INSTRUCTIONS: Create mock exam attempt data in your edx exams admin (If developing locally, this is located at http://localhost:18740/admin/core/examattempt/). In an incognito window, log in to a staff or instructor account Go to the course view for the course you are testing (the one with all the checkboxes and collapsable course sections), then navigating to the "Instructor" tab to get to the Instructor Dashboard, then navigating to the "Special Exams" tab within the Instructor dashboard.

#. Clicking on the "Special Exams" tab should load the *new* version of the exams dashboard
    - The old version has two collapsable sections titled "Allowance Section" and "Student Special Exam Attempts"
    - The new version has a dropdown selector labelled "Select an Exam", with two tabs below it that say "Attempts" and "Review Dashboard"
#. Clicking on the "Review Dashboard" tab within the exams dashboard should display a button labelled "View resource in a new window"
#. Clicking this button should open a dashboard owned by your selected procotoring software (e.g. a Proctortrack or Proctorio dashboard for reviewing exam attempt details) in a new tab
#. Return to the exams dashboard and select the "Attempts" tab. Clicking the "Select An Exam" dropdown should show the list of exams for the course
#. Filtering by exam name in the exam selection dropdown should bring up the expected exams (e.g. querying "M4-M6" shows all the exams in that section)
#. Selecting a specific exam (i.e. the ones you just took) should load the respective exam attempts for those exams
#. The exam attempts should be in the expected status, e.g. successful attempts are submitted or verified, and the errored attempts are errored
#. Filtering by username only should show exam attempts for that username
#. Clicking the "Review Dashboard" link in the modal should load the review dashboard for your chosen Proctoring Software (e.g. Proctortrack or Proctorio)

Can Reject/Verify "Review Required" attempts
--------------------------------------------
INSTRUCTIONS: Go into another exam and be suspiscious. Block your webcam, leave for a few seconds, make strange noises, open a bunch of tabs, watch some youtube, open wikipedia, ask chatgpt for the answer to life, etc. Note you will need to do this a couple of times

#. Submit your suspiscious exam attempt, and check the exams dashboard. Assuming you were suspiscious enough, you should see a row that has a status of "Review Required" AND has a "Review Required" button for your attempt
    #. NOTE: This exam attempt may appear with the status "Satisfied" if you are using Proctorio. This means Proctorio's system is still analyzing your attempt. If this happens, just wait a bit and refresh the page until the status changes to "Verified"
#. Clicking the "Review Required" button should spawn a modal that says "Update review status"
#. Clicking "Cancel" should close the modal
#. Clicking "Verify" should mark attempt as verified the dashboard
#. Check the Gradebook (Instructor Dashboard -> Student Admin -> Gradebook) and check that the grade for the exam is 100
#. Clicking "Reject" should mark attempt as reject the dashboard
#. Check the Gradebook (Instructor Dashboard -> Student Admin -> Gradebook) and check that the grade for the exam is 0

Can Review Verified Attempts
----------------------------
INSTRUCTIONS: Go into another exam and don't be suspiscious. Keep your webcam on with your face in frame. Complete the exam

#. An exam attempt with a status of "Verified" should appear and have a button/link at the end of their rows titled "Manual Review"
    #. NOTE: This exam attempt may appear with the status "Satisfied" if you are using Proctorio. This means Proctorio's system is still analyzing your attempt. If this happens, just wait a bit and refresh the page until the status changes to "Verified"
#. A modal should pop up upon clicking "Manual Review" that contains "Cancel" and "Reject" Buttons
#. Clicking "Cancel" should close the modal
#. Clicking "Reject" should change the attempt status to "rejected" in the UI
#. Check the Gradebook (Instructor Dashboard -> Student Admin -> Gradebook) and check that the grade for the exam is 0
#. Check the Generated Certificates table in the LMS admin at "{your platform url}/admin/certificates/generatedcertificate/" to see if the user's certificate for the course has been marked as "invalidated"

Can Review Rejected Attempts
----------------------------
#. The exam attempt that you just marked as "Rejected" should have a button at the end of their rows saying "Manual Review"
#. A modal pops up upon clicking "Manual Review" that should only have the "Cancel" and "Verify" Buttons
#. Clicking "Cancel" should close the modal
#. Clicking "Verify" should change the attempt status to "verified" in the UI
#. Check the Gradebook (Instructor Dashboard -> Student Admin -> Gradebook) and check that the grade for the exam is 100


Can Reset Errored Exam Attempts
===============================
INSTRUCTIONS: Using Proctorio, start a new exam in your learner account, then open Chrome devtools using Cmd+Option+I on Mac (F12 on Windows).

#. If you don't happen to be using Proctorio, you will need to find a way to error out your exam and test that the expected behavior occurs.
#. The exam should error out the exam and load a "Error with proctored exam" page
#. If you are using Proctorio, this should open the "Proctorio Support" page in another tab
#. In your admin account, go to the exams dashboard. The respective exam attempt should appear in the exams dashboard with the status "Error"
#. Clicking the "Reset" link/button on the exam attempt should bring up a confirmation modal
#. Clicking "No (Cancel)" should close the modal
#. Clicking "Yes I'm Sure" should remove the exam attempt from the table (confirming that it's been reset)
#. The learner's completion status for the exam should be reset (i.e. the green checkmark is now gone)
#. As a learner, try taking the exam again. You should be brought to the initial interstitials, as though this were your first time taking the exam.
