# Attendence/__init__.py
"""
Attendence package initializer.
"""
import logging
logging.captureWarnings(True)

from .admin import show_admin_panel
from .analytics import show_analytics_panel
from .student import show_student_panel
