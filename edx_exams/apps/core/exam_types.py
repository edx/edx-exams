"""
This module defines a set of exam types
"""


class ExamType:
    """
    A collection of properties that describe a specific type of exam
    """
    name = None
    is_proctored = False
    is_timed = False
    is_practice = False


class ProctoredExamType(ExamType):
    """
    Properties for a proctored exam
    """
    name = 'proctored'
    description = 'Non-practice, timed, proctored exam'
    is_proctored = True
    is_timed = True
    is_practice = False


class TimedExamType(ExamType):
    """
    Properties for a timed exam
    """
    name = 'timed'
    description = 'Non-practice, non-proctored, timed exam'
    is_proctored = False
    is_timed = True
    is_practice = False


class PracticeExamType(ExamType):
    """
    Properties for practice exam
    """
    name = 'practice'
    description = 'Practice, non-proctored, timed exam'
    is_proctored = False
    is_timed = True
    is_practice = True


class OnboardingExamType(ExamType):
    """
    Properties for proctored onboarding exam
    """
    name = 'onboarding'
    description = 'Practice, timed, proctored exam'
    is_proctored = True
    is_timed = True
    is_practice = True


EXAM_TYPES = [
  ProctoredExamType,
  TimedExamType,
  PracticeExamType,
  OnboardingExamType,
]


def get_exam_type(name):
    """
    Return the correct class based on a given exam type name
    """
    for exam_type in EXAM_TYPES:
        if name == exam_type.name:
            return exam_type

    return None
