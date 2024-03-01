""" Tests for bulk_add_course_staff management command """
from tempfile import NamedTemporaryFile

from django.core.management import call_command
from django.test import TestCase

from edx_exams.apps.core.models import CourseStaffRole
from edx_exams.apps.core.test_utils.factories import UserFactory


class TestBulkAddCourseStaff(TestCase):
    """ Test bulk_add_course_staff management command """

    def setUp(self):
        super().setUp()
        self.command = 'bulk_add_course_staff'
        self.success_log_message = 'Bulk add course staff complete!'

        # create existing user
        self.user = UserFactory.create(
            username='amy',
            is_active=True,
            is_staff=True,
        )
        self.user.email = 'amy@pond.com'
        self.user.save()

        self.course_id = 'course-v1:edx+test+f19'

    def _write_test_csv(self, csv, lines):
        """ Write a test csv file with the lines provided """
        csv.write(b'username,email,role,course_id\n')
        for line in lines:
            csv.write(line.encode())
        csv.seek(0)
        return csv

    def test_empty_csv(self):
        lines = []
        with NamedTemporaryFile() as csv:
            csv = self._write_test_csv(csv, lines)
            call_command(self.command, f'--csv_path={csv.name}')

    def test_add_course_staff_with_existing_user(self):
        lines = ['amy,amy@pond.com,staff,course-v1:edx+test+f19\n']
        with NamedTemporaryFile() as csv:
            csv = self._write_test_csv(csv, lines)
            call_command(self.command, f'--csv_path={csv.name}')
            assert CourseStaffRole.objects.filter(user=self.user.id).exists()

    def test_add_course_staff_with_new_user(self):
        lines = ['pam,pam@pond.com,staff,course-v1:edx+test+f20\n']
        with NamedTemporaryFile() as csv:
            csv = self._write_test_csv(csv, lines)
            call_command(self.command, f'--csv_path={csv.name}')
            assert CourseStaffRole.objects.filter(course_id='course-v1:edx+test+f20').count() == 1

    def test_add_course_staff_with_not_default_batch_size(self):
        lines = ['pam,pam@pond.com,staff,course-v1:edx+test+f20\n',
                 'sam,sam@pond.com,staff,course-v1:edx+test+f20\n']
        with NamedTemporaryFile() as csv:
            csv = self._write_test_csv(csv, lines)
            call_command(self.command, f'--csv_path={csv.name}', '--batch_size=1')
            assert CourseStaffRole.objects.filter(course_id='course-v1:edx+test+f20').count() == 2

    def test_add_course_staff_with_not_default_batch_delay(self):
        lines = ['pam,pam@pond.com,staff,course-v1:edx+test+f20\n',
                 'sam,sam@pond.com,staff,course-v1:edx+test+f20\n']
        with NamedTemporaryFile() as csv:
            csv = self._write_test_csv(csv, lines)
            call_command(self.command, f'--csv_path={csv.name}', '--batch_size=1', '--batch_delay=2')
            assert CourseStaffRole.objects.filter(course_id='course-v1:edx+test+f20').count() == 2

    def test_num_queries_correct(self):
        """
        Expect the number of queries to be 5 + 1 * number of lines
        - 2 for savepoint/release savepoint, 1 to get existing usernames,
        - 1 to bulk create users, 1 to bulk create course role
        - 1 for each user (to get user)
        """
        num_lines = 20
        lines = [f'pam{i},pam{i}@pond.com,staff,course-v1:edx+test+f20\n' for i in range(num_lines)]
        with NamedTemporaryFile() as csv:
            csv = self._write_test_csv(csv, lines)
            with self.assertNumQueries(5 + num_lines):
                call_command(self.command, f'--csv_path={csv.name}')
