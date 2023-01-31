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
