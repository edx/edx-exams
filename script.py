import datetime

from edx_exams.apps.core.models import ExamAttempt, Exam, AssessmentControlResult
from edx_exams.apps.api.test_utils.factories import UserFactory
from edx_exams.apps.core.statuses import ExamAttemptStatus

import string
import random

# Set this to however many exams you want to add
DEFUALT_ATTEMPT_AMOUNT = 5


def insert(manual_amount=None):
    exam = Exam.objects.get(
        resource_id='2505b63c-1793-41e6-acf9-94007905cea9',
        course_id='course-v1:edx+M3ISBEINGTESTED+WAHOO',
        content_id='block-v1:edx+M3ISBEINGTESTED+WAHOO+type@sequential+block@37ba91669a0c415299b6c4f5165c8b3f',
    )

    print('EXAM:', exam)
    if manual_amount:
        attempt_amount = manual_amount
    else:
        attempt_amount = DEFUALT_ATTEMPT_AMOUNT

    for i in range(0, attempt_amount):
        N = 7
        username = ''.join(random.choices(string.ascii_letters, k=N))
        user = UserFactory(username=username)

        attempt = ExamAttempt.objects.create(
            user=user,
            exam=exam,
            attempt_number=1,
            status=ExamAttemptStatus.second_review_required,
            start_time=datetime.datetime.now() - datetime.timedelta(minutes=56),
            end_time=datetime.datetime.now(),
            allowed_time_limit_mins=60,
        )

        AssessmentControlResult.objects.create(
            attempt=attempt,
            action_type='terminate',
            incident_time=datetime.datetime.now(),
            severity=1.0,
            reason_code='1',
        )

    print('done')
