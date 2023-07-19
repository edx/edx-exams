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

    # the exam has received a high suspicion score and should be reviewed
    second_review_required = 'second_review_required'

    # the exam has been rejected
    rejected = 'rejected'

    # the course end date has passed
    expired = 'expired'

    # the exam attempt requires a secondary review to verify its integrity
    second_review_required = 'second_review_required'

    # the exam has errored
    error = 'error'

    # list of all statuses for active/in-progress exam attempts
    in_progress_statuses = [started, ready_to_submit]

    # list of all statuses considered completed
    completed_statuses = [timed_out, submitted, verified, rejected, error, second_review_required]

    # list of all statuses considered incomplete
    incomplete_statuses = [created, download_software_clicked, ready_to_start, started, ready_to_submit]

    @classmethod
    def is_completed_status(cls, status):
        """
        Returns a boolean if the passed in status is in a "completed" state, meaning
        that it cannot go backwards in state
        """
        return status in cls.completed_statuses

    @classmethod
    def is_incomplete_status(cls, status):
        """
        Returns a boolean if the passed in status is in an "incomplete" state.
        """
        return status in cls.incomplete_statuses

    @classmethod
    def is_status_transition_legal(cls, from_status, to_status):
        """
        Determine and return as a boolean whether a proctored exam attempt state transition
        from from_status to to_status is an allowed state transition.

        Arguments:
            from_status: original status of a proctored exam attempt
            to_status: future status of a proctored exam attempt
        """

        in_completed_status = cls.is_completed_status(from_status)
        to_incomplete_status = cls.is_incomplete_status(to_status)

        # don't allow state transitions from a completed state to an incomplete state
        if in_completed_status and to_incomplete_status:
            return False
        return True
