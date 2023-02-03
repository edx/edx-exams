"""
API Utilities
"""
import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from edx_exams.apps.core.exceptions import ExamBaseException

log = logging.getLogger(__name__)


def handle_exam_exception(exc, name=None):  # pylint: disable=inconsistent-return-statements
    """
    Converts exam exceptions into restframework responses
    """
    if isinstance(exc, ExamBaseException):
        log.exception(name)
        return Response(status=exc.http_status, data={'detail': str(exc)})


class ExamsAPIView(APIView):
    """
    Overrides APIView to handle exams exceptions
    """
    def handle_exception(self, exc):
        """
        Converts proctoring exceptions into standard restframework responses
        """
        resp = handle_exam_exception(exc, name=self.__class__.__name__)
        if not resp:
            resp = super().handle_exception(exc)
        return resp
