"""
edX Exams Signal Handlers
"""
from django.dispatch import receiver
# from lti_consumer.signals.signals import LTI_1P3_PROCTORING_ASSESSMENT_STARTED


# @receiver(LTI_1P3_PROCTORING_ASSESSMENT_STARTED)
def assessment_started(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Signal handler for the lti_consumer LTI_1P3_PROCTORING_ASSESSMENT_STARTED signal.
    """
    print(f"LTI_1P3_PROCTORING_ASSESSMENT_STARTED signal received with kwargs: {kwargs}")
