import datetime

from edx_exams.apps.core.models import (
    ExamAttempt,
    Exam,
    CourseExamConfiguration,
    ProctoringProvider,
)
from edx_exams.apps.api.test_utils.factories import UserFactory
from edx_exams.apps.core.statuses import ExamAttemptStatus


# Set this to however many exams you want to add
ATTEMPT_AMOUNT = 10


def insert():
    exam = Exam.objects.get(
        resource_id="c49f03cd-d6f7-4c0f-a9cb-ec613a24a607",
        course_id='course-v1:edx+M3ISBEINGTESTED+WAHOO',
        content_id='block-v1:edx+M3ISBEINGTESTED+WAHOO+type@sequential+block@28b02a907316428f9a7eb0e4fe64bb05',
    )


    print("EXAM:", exam)
    user = UserFactory(username='verified')

    # for i in range(0, ATTEMPT_AMOUNT):
    ExamAttempt.objects.create(
        user=user,
        exam=exam,
        attempt_number=1,
        status=ExamAttemptStatus.submitted,
        start_time=datetime.datetime.now() - datetime.timedelta(minutes=56),
        end_time=datetime.datetime.now(),
        allowed_time_limit_mins=60,
    )

    print("done")
