"""Management command to populate the CourseStaffRole model and related User objects, from LMS, using CSV"""
import csv
import logging
import time

from django.core.management.base import BaseCommand
from django.db import transaction

from edx_exams.apps.core.models import CourseStaffRole, User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Management command to add Course Staff (and User) in batches from CSV
    """
    help = """
    Add Course Staff in bulk from CSV.
    Expects that the data will be provided in a csv file format with the first row
    being the header and columns being: username, email, role, course_id.
    Examples:
        $ ... bulk_add_course_staff --csv_path=foo.csv
        $ ... bulk_add_course_staff --csv_path=foo.csv --batch_size=100 --batch_delay=2
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-p', '--csv_path',
            metavar='csv_path',
            dest='csv_path',
            required=True,
            help='Path to CSV file.')
        parser.add_argument(
            '--batch_size',
            type=int,
            default=200,
            dest='batch_size',
            help='Batch size')
        parser.add_argument(
            '--batch_delay',
            type=float,
            default=1.0,
            dest='batch_delay',
            help='Time delay in seconds for each batch')

    @transaction.atomic
    def handle(self, *args, **options):
        """
        The main logic and entry point of the management command
        """
        csv_path = options['csv_path']
        batch_size = options['batch_size']
        batch_delay = options['batch_delay']

        with open(csv_path, 'r') as csv_file:
            self.add_course_staff_from_csv(csv_file, batch_size, batch_delay)

        logger.info('Bulk add course staff complete!')

    def add_course_staff_from_csv(self, csv_file, batch_size, batch_delay):
        """
        Add the given set of course staff provided in csv
        """
        reader = list(csv.DictReader(csv_file))
        users_to_create = []
        users_existing = {u.username for u in User.objects.filter(username__in=[r.get('username') for r in reader])}
        for row in reader:
            if row.get('username') not in users_existing:
                users_to_create.append(row)
                users_existing.add(row.get('username'))

        # bulk create users
        for i in range(0, len(users_to_create), batch_size):
            User.objects.bulk_create(
                User(
                    username=user.get('username'),
                    email=user.get('email'),
                )
                for user in users_to_create[i:i + batch_size]
            )
            time.sleep(batch_delay)

        # bulk create course staff
        for i in range(0, len(reader), batch_size):
            CourseStaffRole.objects.bulk_create(
                CourseStaffRole(
                    user=User.objects.get(username=row.get('username')),
                    course_id=row.get('course_id'),
                    role=row.get('role'),
                )
                for row in reader[i:i + batch_size]
            )
            time.sleep(batch_delay)
