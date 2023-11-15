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
        resource_id='c661ca6c-ed08-42bd-bdc8-50c8c55ec6b1',
        course_id='course-v1:edX+TEST101+2024',
        content_id='block-v1:edX+TEST101+2024+type@sequential+block@0b1465cfce42435da197741b5a81600f',
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
            status=ExamAttemptStatus.error,
            # status=ExamAttemptStatus.second_review_required,
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
