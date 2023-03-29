"""
Custom exceptions for edx-exams
"""
from rest_framework import status


class ExamBaseException(Exception):
    """
    A common base class for all exceptions
    """
    http_status = status.HTTP_400_BAD_REQUEST


class ExamIllegalStatusTransition(ExamBaseException):
    """
    Raised if a state transition is not allowed, e.g. going from submitted to started or trying
    to start an already started exam
    """


class ExamAttemptOnPastDueExam(ExamBaseException):
    """
    Raised if a student tries to create an exam attempt for a non-practice exam whose
    due date has already passed
    """


class ExamDoesNotExist(ExamBaseException):
    """
    Raised if trying to access an exam that does not exist
    """


class ExamAttemptAlreadyExists(ExamBaseException):
    """
    Raised when trying to start an exam when an Exam Attempt already exists.
    """
