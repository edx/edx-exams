"""
Serializers for the edx-exams API
"""
from rest_framework import serializers

from edx_exams.apps.core.exam_types import EXAM_TYPES
from edx_exams.apps.core.models import Exam


class ExamSerializer(serializers.ModelSerializer):
    """
    Serializer for the Exam Model
    """

    exam_name = serializers.CharField(required=True)
    course_id = serializers.CharField(required=False)
    content_id = serializers.CharField(required=True)
    time_limit_mins = serializers.IntegerField(required=True)
    due_date = serializers.DateTimeField(required=False, format=None)
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
