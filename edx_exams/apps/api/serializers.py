"""
Serializers for the edx-exams API
"""
from rest_framework import serializers
from rest_framework.fields import DateTimeField

from edx_exams.apps.core.api import get_exam_url_path, get_exam_attempt_time_remaining
from edx_exams.apps.core.exam_types import EXAM_TYPES
from edx_exams.apps.core.models import Exam, ExamAttempt, ProctoringProvider, User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User Model.
    """
    id = serializers.IntegerField(required=False)  # pylint: disable=invalid-name
    lms_user_id = serializers.IntegerField(required=False)
    username = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        """
        Meta Class
        """
        model = User

        fields = (
            "id", "username", "email", "lms_user_id"
        )


class ExamSerializer(serializers.ModelSerializer):
    """
    Serializer for the Exam Model
    """

    exam_name = serializers.CharField(required=True)
    course_id = serializers.CharField(required=False)
    content_id = serializers.CharField(required=True)
    time_limit_mins = serializers.IntegerField(required=True)
    due_date = serializers.DateTimeField(required=True, format=None, allow_null=True)
    exam_type = serializers.CharField(required=True)
    hide_after_due = serializers.BooleanField(required=True)
    is_active = serializers.BooleanField(required=True)

    class Meta:
        """
        Meta Class
        """

        model = Exam

        fields = (
            "id", "exam_name", "course_id", "content_id", "time_limit_mins", "due_date", "exam_type",
            "hide_after_due", "is_active",
        )

    def validate_exam_type(self, value):
        """
        Validate that exam_type is one of the predefined choices
        """
        valid_exam_types = [exam_type.name for exam_type in EXAM_TYPES]
        if value not in valid_exam_types:
            raise serializers.ValidationError("Must be a valid exam type.")
        return value


class ProctoringProviderSerializer(serializers.ModelSerializer):
    """
        Serializer for the ProctoringProvider Model
    """

    class Meta:
        model = ProctoringProvider
        fields = ["name", "verbose_name", "lti_configuration_id"]


class ExamAttemptSerializer(serializers.ModelSerializer):
    """
    Serializer for the ExamAttempt Model
    """
    exam = ExamSerializer()
    user = UserSerializer()

    start_time = DateTimeField(format=None)
    end_time = DateTimeField(format=None)

    class Meta:
        """
        Meta Class
        """
        model = ExamAttempt

        fields = (
            "id", "created", "modified", "user", "start_time", "end_time",
            "status", "exam", "allowed_time_limit_mins", "attempt_number"
        )


class StudentAttemptSerializer(serializers.ModelSerializer):
    """
    Serializer for the ExamAttempt model containing additional fields needed for the frontend UI
    """
    # directly from the ExamAttempt Model
    attempt_id = serializers.IntegerField(source='id')
    attempt_status = serializers.CharField(source='status')

    # custom fields based on the ExamAttemptModel
    course_id = serializers.SerializerMethodField()
    exam_type = serializers.SerializerMethodField()
    exam_display_name = serializers.SerializerMethodField()
    exam_url_path = serializers.SerializerMethodField()
    time_remaining_seconds = serializers.SerializerMethodField()

    def get_course_id(self, obj):
        return obj.exam.course_id

    def get_exam_type(self, obj):
        return obj.exam.exam_type

    def get_exam_display_name(self, obj):
        return obj.exam.exam_name

    def get_exam_url_path(self, obj):
        course_id = obj.exam.course_id
        content_id = obj.exam.content_id

        return get_exam_url_path(course_id, content_id)

    def get_time_remaining_seconds(self, obj):
        return get_exam_attempt_time_remaining(obj)

    class Meta:
        """
        Meta Class
        """
        model = ExamAttempt

        fields = (
            "id", "status"
        )
