""" Core models. """

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from edx_exams.apps.core.exam_types import EXAM_TYPES


class User(AbstractUser):
    """
    Custom user model for use with python-social-auth via edx-auth-backends.

    .. pii: Stores full name, username, and email address for a user.
    .. pii_types: name, username, email_address
    .. pii_retirement: local_api

    """
    full_name = models.CharField(_('Full Name'), max_length=255, blank=True, null=True)
    lms_user_id = models.IntegerField(null=True, db_index=True)

    anonymous_user_id = models.IntegerField(null=True, db_index=True)

    @property
    def access_token(self):
        """
        Returns an OAuth2 access token for this user, if one exists; otherwise None.
        Assumes user has authenticated at least once with the OAuth2 provider (LMS).
        """
        try:
            return self.social_auth.first().extra_data['access_token']  # pylint: disable=no-member
        except Exception:  # pylint: disable=broad-except
            return None

    class Meta:
        get_latest_by = 'date_joined'

    def get_full_name(self):
        return self.full_name or super().get_full_name()

    def __str__(self):
        return str(self.get_full_name())


class ProctoringProvider(TimeStampedModel):
    """
    Information about the Proctoring Provider

    .. no_pii:
    """

    name = models.CharField(max_length=255, db_index=True)

    verbose_name = models.CharField(max_length=255, db_index=True)

    lti_configuration_id = models.CharField(max_length=255, db_index=True)

    class Meta:
        """ Meta class for this Django model """
        db_table = 'exams_proctoringprovider'
        verbose_name = 'proctoring provider'


class Exam(TimeStampedModel):
    """
    Information about the Exam.

    .. no_pii:
    """

    EXAM_CHOICES = (
        (exam_type.name, exam_type.description)
        for exam_type in EXAM_TYPES
    )

    resource_id = models.CharField(max_length=255, db_index=True)

    course_id = models.CharField(max_length=255, db_index=True)

    provider = models.ForeignKey(ProctoringProvider, on_delete=models.CASCADE, null=True)

    # pointer to the id of the piece of course_ware that is the proctored exam.
    content_id = models.CharField(max_length=255, db_index=True)

    # display name of the Exam (Midterm etc).
    exam_name = models.TextField()

    # type of Exam (proctored, practice, etc).
    exam_type = models.CharField(max_length=255, choices=EXAM_CHOICES, db_index=True)

    # Time limit (in minutes) that a student can finish this exam.
    time_limit_mins = models.PositiveIntegerField()

    # Due date is a deadline to finish the exam
    due_date = models.DateTimeField(null=True)

    # Whether to hide this exam after the due date
    hide_after_due = models.BooleanField(default=False)

    # Whether this exam will be active.
    is_active = models.BooleanField(default=False)

    class Meta:
        """ Meta class for this Django model """
        db_table = 'exams_exam'
        verbose_name = 'exam'
        unique_together = (('course_id', 'content_id', 'exam_type', 'provider'),)


class ExamAttempt(TimeStampedModel):
    """
    Information about the Exam Attempt

    .. no_pii:
    """

    user = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE)

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

    attempt_number = models.PositiveIntegerField()

    status = models.CharField(max_length=64)

    start_time = models.DateTimeField(null=True)

    allowed_time_limit_mins = models.IntegerField(null=True)

    class Meta:
        """ Meta class for this Django model """
        db_table = 'exams_examattempt'
        verbose_name = 'exam attempt'


class CourseExamConfiguration(TimeStampedModel):
    """
    Information about the Course Exam Configuration

    .. no_pii:
    """

    course_id = models.CharField(max_length=255, db_index=True, unique=True)

    provider = models.ForeignKey(ProctoringProvider, on_delete=models.CASCADE)

    allow_opt_out = models.BooleanField(default=False)

    class Meta:
        """ Meta class for this Django model """
        db_table = 'exams_courseexamconfiguration'
        verbose_name = 'course exam configuration'
