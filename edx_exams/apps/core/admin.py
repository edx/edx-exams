""" Admin configuration for core models. """

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CourseExamConfiguration, Exam, ExamAttempt, ProctoringProvider, User


class CustomUserAdmin(UserAdmin):
    """ Admin configuration for the custom User model. """
    list_display = ('username', 'email', 'full_name', 'first_name', 'last_name', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


class ProctoringProviderAdmin(admin.ModelAdmin):
    """ Admin configuration for the Proctoring Provider model """
    list_display = ('name', 'verbose_name', 'lti_configuration_id')
    search_fields = ('name', 'verbose_name', 'lti_configuration_id')
    ordering = ('name',)


class ExamAdmin(admin.ModelAdmin):
    """ Admin configuration for the Exam model """
    list_display = ('resource_id', 'course_id', 'provider', 'content_id', 'exam_name',
                    'exam_type', 'time_limit_mins', 'due_date', 'hide_after_due', 'is_active')
    search_fields = ('resource_id', 'course_id', 'provider__name', 'content_id', 'exam_name',
                     'exam_type', 'time_limit_mins', 'due_date', 'hide_after_due', 'is_active')
    ordering = ('course_id', 'exam_name',)


class ExamAttemptAdmin(admin.ModelAdmin):
    """ Admin configuration for the Exam Attempt model """
    list_display = ('user', 'exam', 'attempt_number', 'status', 'start_time',
                    'allowed_time_limit_mins')
    search_fields = ('user__username', 'attempt_number')
    ordering = ('-modified',)


class CourseExamConfigurationAdmin(admin.ModelAdmin):
    """ Admin configuration for the Course Exam Configuration model """
    list_display = ('course_id', 'provider', 'allow_opt_out')
    search_fields = ('course_id', 'provider__name', 'allow_opt_out')
    ordering = ('course_id',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(ProctoringProvider, ProctoringProviderAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(ExamAttempt, ExamAttemptAdmin)
admin.site.register(CourseExamConfiguration, CourseExamConfigurationAdmin)
