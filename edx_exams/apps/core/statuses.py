"""
Status enums for edx-exams
"""


class ExamAttemptStatus:
    """
    A class to enumerate the various statuses that an exam attempt can have
    """
    # the attempt record has been created, but the exam has not yet
    # been started
    created = 'created'

    # the student has clicked on the external
    # software download link
    download_software_clicked = 'download_software_clicked'

    # the attempt is ready to start but requires
    # user to acknowledge that he/she wants to start the exam
    ready_to_start = 'ready_to_start'

    # the student has started the exam and is
    # in the process of completing the exam
    started = 'started'

    # the student has completed the exam
    ready_to_submit = 'ready_to_submit'

    # the exam has timed out
    timed_out = 'timed_out'

    # the student has submitted the exam for proctoring review
    submitted = 'submitted'

    # the exam has been verified and approved
    verified = 'verified'

    # the exam has been rejected
    rejected = 'rejected'

    # the course end date has passed
    expired = 'expired'
