""" Tests for bulk_add_course_staff management command """
from tempfile import NamedTemporaryFile

from django.core.management import call_command
from django.test import TestCase

from edx_exams.apps.core.models import CourseStaffRole, User
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
        self.course_role = 'staff'

    def _write_test_csv(self, csv, lines):
        """ Write a test csv file with the lines provided """
        csv.write(b'username,email,role,course_id\n')
        for line in lines:
            csv.write(line.encode())
        csv.seek(0)
        return csv

    def _assert_user_and_role(self, username, email, course_role, course_id):
        """ Helper that asserts that User and CourseStaffRole are created """
        user = User.objects.filter(username=username, email=email)
        assert user.exists()
        assert CourseStaffRole.objects.filter(
            user=user[0].id,
            course_id=course_id,
            role=course_role,
        ).exists()

    def test_empty_csv(self):
        lines = []
        with NamedTemporaryFile() as csv:
            csv = self._write_test_csv(csv, lines)
            call_command(self.command, f'--csv_path={csv.name}')
            assert not CourseStaffRole.objects.filter(
                user=self.user.id,
                course_id=self.course_id,
                role=self.course_role,
            ).exists()

    def test_add_course_staff_with_existing_user(self):
        lines = [f'{self.user.username},{self.user.email},{self.course_role},{self.course_id}\n']
        with NamedTemporaryFile() as csv:
            csv = self._write_test_csv(csv, lines)
            call_command(self.command, f'--csv_path={csv.name}')
            self._assert_user_and_role(self.user.username, self.user.email, self.course_role, self.course_id)

    def test_add_course_staff_with_new_user(self):
        username, email = 'pam', 'pam@pond.com'
        lines = [f'{username},{email},{self.course_role},{self.course_id}\n']
        with NamedTemporaryFile() as csv:
            csv = self._write_test_csv(csv, lines)
            call_command(self.command, f'--csv_path={csv.name}')
            self._assert_user_and_role(username, email, self.course_role, self.course_id)

    def test_add_course_staff_multiple(self):
        """ Assert that the course staff role is correct given multiple lines """
        username, email = 'pam', 'pam@pond.com'
        username2, email2 = 'cam', 'cam@pond.com'
        lines = [f'{username},{email},{self.course_role},{self.course_id}\n',
                 f'{username2},{email2},{self.course_role},{self.course_id}\n']
        with NamedTemporaryFile() as csv:
            csv = self._write_test_csv(csv, lines)
            call_command(self.command, f'--csv_path={csv.name}')
            self._assert_user_and_role(username, email, self.course_role, self.course_id)
            self._assert_user_and_role(username2, email2, self.course_role, self.course_id)

    def test_add_course_staff_with_not_default_batch_size(self):
        """ Assert that the number of queries is correct given 2 batches """
        lines = ['pam,pam@pond.com,staff,course-v1:edx+test+f20\n',
                 'sam,sam@pond.com,staff,course-v1:edx+test+f20\n']
        with NamedTemporaryFile() as csv:
            csv = self._write_test_csv(csv, lines)
            with self.assertNumQueries(9):
                call_command(self.command, f'--csv_path={csv.name}', '--batch_size=1')

    def test_add_course_staff_with_not_default_batch_delay(self):
        username, email = 'pam', 'pam@pond.com'
        username2, email2 = 'cam', 'cam@pond.com'
        lines = [f'{username},{email},{self.course_role},{self.course_id}\n',
                 f'{username2},{email2},{self.course_role},{self.course_id}\n']
        with NamedTemporaryFile() as csv:
            csv = self._write_test_csv(csv, lines)
            call_command(self.command, f'--csv_path={csv.name}', '--batch_size=1', '--batch_delay=2')
            self._assert_user_and_role(username, email, self.course_role, self.course_id)
            self._assert_user_and_role(username2, email2, self.course_role, self.course_id)

    def test_num_queries_correct(self):
        """
        Assert the number of queries to be 5 + 1 * number of lines:
        2 for savepoint/release savepoint, 1 to get existing usernames,
        1 to bulk create users, 1 to bulk create course role
        1 for each user (to get user)
        """
        num_lines = 20
        lines = [f'pam{i},pam{i}@pond.com,staff,course-v1:edx+test+f20\n' for i in range(num_lines)]
        with NamedTemporaryFile() as csv:
            csv = self._write_test_csv(csv, lines)
            with self.assertNumQueries(5 + num_lines):
                call_command(self.command, f'--csv_path={csv.name}')
