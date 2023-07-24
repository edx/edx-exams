"""
Constants for the edx_exams API.
"""

ASSESSMENT_CONTROL_CODES = {
    '0':  'Disconnected from proctoring',
    '1':  'Submitted by user',
    '2':  'Navigated away from assessment',
    '4':  'Left exam when in full screen',
    '5':  'Ended screen recording',
    '6':  'Uninstalled browser extension',
    '7':  'Switched to a proxy during exam',
    '8':  'Changed networks during exam',
    '9':  'Closed or reloaded the exam tab',
    '12': 'Attempted to modify the exam page',
    '13': 'Attempted to download a file during exam',
    '14': 'The battery died on learner\'s device',
    '15': 'Plugged in additional monitors',
    '16': 'Unplugged camera or microphone',
    '21': 'Page became unresponsive during exam',
    '24': 'Revoked microphone permissions',
    '25': 'Revoked camera permissions',
}
