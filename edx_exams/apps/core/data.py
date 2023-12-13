"""
Public data structures for the core applictaion.
"""
from attrs import field, frozen, validators


@frozen
class CourseExamConfigurationData:
    course_id: str = field(validator=validators.instance_of(str))
    provider: str = field(validator=validators.instance_of(str))
    allow_opt_out: field(validator=validators.instance_of(str))
    escalation_email: str = field(validator=validators.instance_of(str))
