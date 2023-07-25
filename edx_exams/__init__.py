"""
edx-exams module.
"""
__version__ = '0.1.0'

import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.test')
django.setup()
