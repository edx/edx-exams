"""
Test event handlers
"""
import uuid
from datetime import datetime, timezone

import ddt
from django.test import TestCase
from openedx_events.data import EventsMetadata
from openedx_events.learning.data import CourseAccessRoleData, UserData, UserPersonalData
from openedx_events.learning.signals import COURSE_ACCESS_ROLE_ADDED, COURSE_ACCESS_ROLE_REMOVED

from edx_exams.apps.core.models import CourseStaffRole, User
from edx_exams.apps.core.signals.handlers import (
    listen_for_course_access_role_added,
    listen_for_course_access_role_removed
)
from edx_exams.apps.core.test_utils.factories import CourseStaffRoleFactory, UserFactory


@ddt.ddt
class TestCourseRoleEvents(TestCase):
    """
    Test course role events
    """
    def setUp(self):
        super().setUp()
        self.course_id = 'course-v1:edx+test+2020'
        self.existing_user = UserFactory(
            username='test_user_exists', email='test_user_exists@example.com'
        )
        self.existing_user_with_staff_role = UserFactory(
            username='test_user_staff', email='test_user_staff@example.com'
        )
        self.existing_user_with_instructor_role = UserFactory(
            username='test_user_instructor', email='test_user_instructor@example.com'
        )

        CourseStaffRoleFactory(
            user=self.existing_user_with_staff_role,
            course_id=self.course_id,
            role='staff',
        )
        CourseStaffRoleFactory(
            user=self.existing_user_with_instructor_role,
            course_id=self.course_id,
            role='instructor',
        )

    @staticmethod
    def _get_event_data(course_id, username, role):
        """ create event data object """
        return CourseAccessRoleData(
            org_key='edx',
            course_key=course_id,
            role=role,
            user=UserData(
                pii=UserPersonalData(
                    username=username,
                    email=f'{username}@example.com',
                ),
                id=123,
                is_active=True,
            ),
        )

    @staticmethod
    def _get_event_metadata(event_signal):
        """ create metadata object for event """
        return EventsMetadata(
            event_type=event_signal.event_type,
            id=uuid.uuid4(),
            minorversion=0,
            source='openedx/lms/web',
            sourcehost='lms.test',
            time=datetime.now(timezone.utc),
        )

    @ddt.data(
        ('test_user_1', 'staff', True),
        ('test_user_2', 'limited_staff', True),
        ('test_user_3', 'instructor', True),
        ('test_user_exists', 'staff', True),
        ('test_user_exists', 'other', False),
        ('test_user_staff', 'staff', True),  # test duplicate event
        ('test_user_staff', 'instructor', True),  # test multiple roles
    )
    @ddt.unpack
    def test_course_access_role_added(self, username, role, expect_staff_access):
        """
        Test CourseStaffRole is created on receiving COURSE_ACCESS_ROLE_ADDED event
        with a role that grants staff access to exams
        """
        role_event_data = self._get_event_data(self.course_id, username, role)
        event_metadata = self._get_event_metadata(COURSE_ACCESS_ROLE_ADDED)
        event_kwargs = {
            'course_access_role_data': role_event_data,
            'metadata': event_metadata,
        }
        listen_for_course_access_role_added(None, COURSE_ACCESS_ROLE_ADDED, **event_kwargs)

        user = User.objects.get(username=username)
        self.assertEqual(user.has_course_staff_permission(self.course_id), expect_staff_access)

    @ddt.data(
        ('test_user_staff', 'staff', False),
        ('test_user_instructor', 'instructor', False),
        ('test_user_staff', 'limited_staff', True),
        ('test_user_staff', 'other', True),
        ('test_user_dne', 'other', False),
    )
    @ddt.unpack
    def test_course_access_role_removed(self, username, role, expect_staff_access):
        """
        Test CourseStaffRole is deleted on receiving COURSE_ACCESS_ROLE_REMOVED event
        """
        role_event_data = self._get_event_data(self.course_id, username, role)
        event_metadata = self._get_event_metadata(COURSE_ACCESS_ROLE_REMOVED)
        event_kwargs = {
            'course_access_role_data': role_event_data,
            'metadata': event_metadata,
        }
        listen_for_course_access_role_removed(None, COURSE_ACCESS_ROLE_REMOVED, **event_kwargs)

        if username == 'test_user_dne':
            # this user should not be created (and therefore has no permissions)
            self.assertFalse(User.objects.filter(username=username).exists())
        else:
            user = User.objects.get(username=username)
            self.assertEqual(user.has_course_staff_permission(self.course_id), expect_staff_access)

    def test_course_access_role_remove_single_role(self):
        """
        Test correct role is removed for user with multiple roles
        """
        CourseStaffRoleFactory(
            user=self.existing_user_with_staff_role,
            course_id=self.course_id,
            role='instructor',
        )

        role_event_data = self._get_event_data(self.course_id, 'test_user_staff', 'staff')
        event_metadata = self._get_event_metadata(COURSE_ACCESS_ROLE_REMOVED)
        event_kwargs = {
            'course_access_role_data': role_event_data,
            'metadata': event_metadata,
        }
        listen_for_course_access_role_removed(None, COURSE_ACCESS_ROLE_REMOVED, **event_kwargs)

        roles = [
            staff_role.role for staff_role in
            CourseStaffRole.objects.filter(user=self.existing_user_with_staff_role)
        ]
        self.assertEqual(
            roles,
            ['instructor']
        )

    def test_course_access_role_email_change(self):
        """
        Test that if a user updates their email, additional course staff roles are able to be added.
        """
        role_event_data = self._get_event_data(self.course_id, self.existing_user.username, 'staff')
        event_metadata = self._get_event_metadata(COURSE_ACCESS_ROLE_ADDED)
        event_kwargs = {
            'course_access_role_data': role_event_data,
            'metadata': event_metadata,
        }
        listen_for_course_access_role_added(None, COURSE_ACCESS_ROLE_ADDED, **event_kwargs)

        self.existing_user.email = 'updated_email@example.com'
        self.existing_user.save()

        other_course = 'course-v1:another-course-2024'
        role_event_data = self._get_event_data(other_course, self.existing_user.username, 'staff')
        event_metadata = self._get_event_metadata(COURSE_ACCESS_ROLE_ADDED)
        event_kwargs = {
            'course_access_role_data': role_event_data,
            'metadata': event_metadata,
        }
        listen_for_course_access_role_added(None, COURSE_ACCESS_ROLE_ADDED, **event_kwargs)

        self.assertEqual(len(CourseStaffRole.objects.filter(user=self.existing_user)), 2)
