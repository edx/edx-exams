""" Core models. """
import logging
import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from edx_exams.apps.core.exam_types import EXAM_TYPES
from edx_exams.apps.core.statuses import ExamAttemptStatus

log = logging.getLogger(__name__)


class User(AbstractUser):
    """
    Custom user model for use with python-social-auth via edx-auth-backends.

    .. pii: Stores full name, username, and email address for a user.
    .. pii_types: name, username, email_address
    .. pii_retirement: local_api

    """
    full_name = models.CharField(_('Full Name'), max_length=255, blank=True, null=True)

    lms_user_id = models.IntegerField(null=True, db_index=True)

    anonymous_user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

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


class ProctoringProvider(TimeStampedModel):
    """
    Information about the Proctoring Provider

    .. no_pii:
    """

    name = models.CharField(max_length=255, db_index=True, unique=True)

    verbose_name = models.CharField(max_length=255, db_index=True)

    lti_configuration_id = models.CharField(max_length=255, db_index=True)

    tech_support_phone = models.CharField(max_length=255, null=True)

    tech_support_email = models.CharField(max_length=255, null=True)

    class Meta:
        """ Meta class for this Django model """
        db_table = 'exams_proctoringprovider'
        verbose_name = 'proctoring provider'

    def __str__(self):      # pragma: no cover
        return self.verbose_name


class Exam(TimeStampedModel):
    """
    Information about the Exam.

    .. no_pii:
    """

    EXAM_CHOICES = (
        (exam_type.name, exam_type.name)
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

    # This is the reference to the SimpleHistory table
    history = HistoricalRecords(table_name='exams_examhistory')

    class Meta:
        """ Meta class for this Django model """
        db_table = 'exams_exam'
        verbose_name = 'exam'

        # Uniqueness constraint to only have one active exam per (course_id, content_id) pair
        constraints = [
            models.UniqueConstraint(fields=['course_id', 'content_id'],
                                    condition=models.Q(is_active=True),
                                    name='only one exam instance active')
        ]

    def __str__(self):      # pragma: no cover
        return self.exam_name

    @classmethod
    def get_exam_by_id(cls, exam_id):
        """
        Return Exam for a given id
        """
        try:
            exam = cls.objects.get(id=exam_id)
        except cls.DoesNotExist:
            exam = None
        return exam


class ExamAttempt(TimeStampedModel):
    """
    Information about the Exam Attempt

    .. no_pii:
    """

    STATUS_CHOICES = [
        ExamAttemptStatus.created,
        ExamAttemptStatus.download_software_clicked,
        ExamAttemptStatus.ready_to_start,
        ExamAttemptStatus.started,
        ExamAttemptStatus.ready_to_submit,
        ExamAttemptStatus.timed_out,
        ExamAttemptStatus.submitted,
        ExamAttemptStatus.verified,
        ExamAttemptStatus.rejected,
        ExamAttemptStatus.expired,
        ExamAttemptStatus.second_review_required,
        ExamAttemptStatus.error,
    ]

    user = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE)

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

    attempt_number = models.PositiveIntegerField()

    status = models.CharField(max_length=64, choices=[(status, status) for status in STATUS_CHOICES])

    start_time = models.DateTimeField(null=True)

    end_time = models.DateTimeField(null=True)

    allowed_time_limit_mins = models.IntegerField(null=True)

    # This is the reference to the SimpleHistory table
    history = HistoricalRecords(table_name='exams_examattempthistory')

    class Meta:
        """ Meta class for this Django model """
        db_table = 'exams_examattempt'
        verbose_name = 'exam attempt'

    @classmethod
    def get_current_exam_attempt(cls, user_id, exam_id):
        """
        Given a user and exam, get the user's latest exam attempt, if exists.
        """
        try:
            exam_attempt = cls.objects.filter(user_id=user_id, exam=exam_id).latest('created')
        except ObjectDoesNotExist:
            exam_attempt = None
        return exam_attempt

    @classmethod
    def get_attempt_by_id(cls, attempt_id):
        """
        Return ExamAttempt for a given id
        """
        try:
            attempt = cls.objects.get(id=attempt_id)
        except cls.DoesNotExist:
            attempt = None
        return attempt

    @classmethod
    def get_latest_attempt_for_user(cls, user_id):
        """
        Return latest ExamAttempt (based on start time) associated with a given user_id

        If start_time does not exist for any attempt, return None
        """
        try:
            attempt = cls.objects.filter(user_id=user_id).latest('start_time', 'created')
        except cls.DoesNotExist:
            attempt = None
        return attempt

    @classmethod
    def check_no_other_active_attempts_for_user(cls, user_id, attempt_id):
        """
        Return true if no active exam attempts exist for the user
        Return false otherwise
        """
        try:
            cls.objects.exclude(id=attempt_id).get(user_id=user_id, status__in=ExamAttemptStatus.in_progress_statuses)
            return False
        except cls.DoesNotExist:
            return True

    @classmethod
    def get_attempt_for_user_with_attempt_number_and_resource_id(cls, user_id, attempt_number, resource_id):
        """
        Retrieve an attempt in an exam described by resource_id for a user described by user_id with a particular
        attempt number described by attempt_number.
        """
        try:
            attempt = ExamAttempt.objects.get(
                user_id=user_id,
                attempt_number=attempt_number,
                exam__resource_id=resource_id
            )
            return attempt
        except cls.DoesNotExist:
            return None
        except cls.MultipleObjectsReturned:
            log.warning(
                f'attempt_number={attempt_number} for user_id={user_id} in exam with resource_id={resource_id} is '
                'associated with multiple attempts.'
            )
            return None


class AssessmentControlResult(TimeStampedModel):
    """
    Information about the exam attempt provided by the proctoring provider
    though the ACS API

    .. no_pii:
    """

    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE)

    action_type = models.CharField(max_length=64, choices=[('terminate', 'terminate')])

    incident_time = models.DateTimeField()

    severity = models.DecimalField(max_digits=3, decimal_places=2)

    reason_code = models.CharField(max_length=64)

    class Meta:
        """ Meta class for this Django model """
        db_table = 'exams_assessmentcontrolresult'
        verbose_name = 'assessment control result'


class CourseExamConfiguration(TimeStampedModel):
    """
    Information about the Course Exam Configuration

    .. no_pii:
    """

    course_id = models.CharField(max_length=255, db_index=True, unique=True)

    provider = models.ForeignKey(ProctoringProvider, on_delete=models.CASCADE, null=True)

    allow_opt_out = models.BooleanField(default=False)

    class Meta:
        """ Meta class for this Django model """
        db_table = 'exams_courseexamconfiguration'
        verbose_name = 'course exam configuration'

    @classmethod
    def get_configuration_for_course(cls, course_id):
        """
        Return exam configuration for a course
        """
        try:
            configuration = cls.objects.get(course_id=course_id)
        except cls.DoesNotExist:
            configuration = None
        return configuration

    @classmethod
    @transaction.atomic
    def create_or_update(cls, provider, course_id):
        """
        Helper method that decides whether to update existing or create new config.

        If the config is being updated with a new provider it has to rebuild all
        existing exams.
        """
        provider_name = provider.name if provider else None
        existing_config = CourseExamConfiguration.get_configuration_for_course(course_id)
        if existing_config:
            if existing_config.provider == provider:
                # nothing to be done
                log.info(f'Course exam configuration course_id={course_id} already has provider={provider_name}')
                return
            count = cls.update_course_config_provider(existing_config, provider)
            log.info(f'Updated course exam configuration course_id={course_id} '
                     + f'to provider={provider_name} and recreated {count} exams')
        else:
            CourseExamConfiguration.objects.create(course_id=course_id, provider=provider)
            log.info(f'Created course exam configuration course_id={course_id}, provider={provider_name}')

    @classmethod
    def update_course_config_provider(cls, existing_config, new_provider):
        """
        If the provider is updated for a course, all existing exams have to be retired
        and duplicates made with the new provider.
        """
        with transaction.atomic():
            exams = Exam.objects.filter(course_id=existing_config.course_id, is_active=True)

            existing_config.provider = new_provider
            existing_config.save()

            # we could bulk update, but that would avoid any django save/update hooks
            # that might be added to these objects later and the number of exams per course
            # will not be high enough to worry about
            for exam in exams:
                # set the original inactive
                exam.is_active = False
                exam.save()
                # use the original to stamp out an active duplicate with the new provider
                exam.pk = None
                exam.is_active = True
                exam.provider = new_provider
                exam.save()
