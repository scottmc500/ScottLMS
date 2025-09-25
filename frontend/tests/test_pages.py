"""
Simple tests for frontend pages
"""

import pytest
import sys
import os
from unittest.mock import patch, Mock

# Add frontend to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestPages:
    """Test frontend pages"""

    @pytest.mark.frontend
    def test_import_dashboard_page(self):
        """Test that dashboard page can be imported"""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("dashboard", "pages/1_Dashboard.py")
            dashboard = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(dashboard)
            # Just check that the module was loaded successfully
            assert dashboard is not None
        except Exception as e:
            pytest.fail(f"Failed to import dashboard page: {e}")

    @pytest.mark.frontend
    def test_import_users_page(self):
        """Test that users page can be imported"""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("users", "pages/2_Users.py")
            users = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(users)
            # Just check that the module was loaded successfully
            assert users is not None
        except Exception as e:
            pytest.fail(f"Failed to import users page: {e}")

    @pytest.mark.frontend
    def test_import_courses_page(self):
        """Test that courses page can be imported"""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("courses", "pages/3_Courses.py")
            courses = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(courses)
            # Just check that the module was loaded successfully
            assert courses is not None
        except Exception as e:
            pytest.fail(f"Failed to import courses page: {e}")

    @pytest.mark.frontend
    def test_import_enrollments_page(self):
        """Test that enrollments page can be imported"""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("enrollments", "pages/4_Enrollments.py")
            enrollments = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(enrollments)
            # Just check that the module was loaded successfully
            assert enrollments is not None
        except Exception as e:
            pytest.fail(f"Failed to import enrollments page: {e}")

    @pytest.mark.frontend
    def test_home_page_import(self):
        """Test that home page can be imported"""
        try:
            import Home
            # Just check that the module was loaded successfully
            assert Home is not None
        except ImportError as e:
            pytest.fail(f"Failed to import home page: {e}")
