""" Constants for the core app. """


class Status:
    """Health statuses."""
    OK = 'OK'
    UNAVAILABLE = 'UNAVAILABLE'


# Pulled from edx-platform. Will correctly capture both old- and new-style
# course ID strings.
INTERNAL_COURSE_KEY_PATTERN = r'([^/+]+(/|\+)[^/+]+(/|\+)[^/?]+)'

EXTERNAL_COURSE_KEY_PATTERN = r'([A-Za-z0-9-_:]+)'

COURSE_ID_PATTERN = rf'(?P<course_id>({INTERNAL_COURSE_KEY_PATTERN}|{EXTERNAL_COURSE_KEY_PATTERN}))'

USAGE_KEY_PATTERN = r'(?P<content_id>(?:i4x://?[^/]+/[^/]+/[^/]+/[^@]+(?:@[^/]+)?)|(?:[^/]+))'

EXAM_ID_PATTERN = r'(?P<exam_id>\d+)'
