"""
Course-related components and forms
"""

from .forms import create_course_form, edit_course_form, delete_course_confirmation

from .tables import display_course_details, display_courses

__all__ = [
    "create_course_form",
    "edit_course_form",
    "delete_course_confirmation",
    "display_course_details",
    "display_courses",
]
