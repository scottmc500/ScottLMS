"""
Tests for entity models and validation
"""

import pytest
import sys
import os
from datetime import datetime
from pydantic import ValidationError

# Add backend to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from entities.users import User, UserCreate, UserUpdate, UserResponse, UserRole
from entities.courses import Course, CourseCreate, CourseUpdate, CourseResponse, CourseStatus
from entities.enrollments import Enrollment, EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse, EnrollmentStatus


class TestUserEntity:
    """Test User entity models"""

    @pytest.mark.backend
    def test_user_create_valid_data(self):
        """Test UserCreate with valid data"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "role": UserRole.STUDENT,
            "password": "password123"
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.role == UserRole.STUDENT

    @pytest.mark.backend
    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email"""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "role": UserRole.STUDENT,
            "password": "password123"
        }
        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    @pytest.mark.backend
    def test_user_create_short_password(self):
        """Test UserCreate with short password"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "role": UserRole.STUDENT,
            "password": "short"
        }
        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    @pytest.mark.backend
    def test_user_update_partial_data(self):
        """Test UserUpdate with partial data"""
        update_data = {
            "first_name": "Updated",
            "is_active": False
        }
        user_update = UserUpdate(**update_data)
        assert user_update.first_name == "Updated"
        assert user_update.is_active is False
        assert user_update.email is None

    @pytest.mark.backend
    def test_user_response_model(self):
        """Test UserResponse model"""
        from beanie import PydanticObjectId
        
        user_data = {
            "id": PydanticObjectId(),
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "role": UserRole.STUDENT,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        user_response = UserResponse(**user_data)
        assert user_response.email == "test@example.com"
        assert user_response.role == UserRole.STUDENT


class TestCourseEntity:
    """Test Course entity models"""

    @pytest.mark.backend
    def test_course_create_valid_data(self):
        """Test CourseCreate with valid data"""
        from beanie import PydanticObjectId
        
        course_data = {
            "title": "Test Course",
            "description": "A test course description",
            "instructor_id": PydanticObjectId(),
            "status": CourseStatus.DRAFT,
            "price": 99.99,
            "duration_hours": 40,
            "max_students": 30,
            "tags": ["python", "programming"]
        }
        course = CourseCreate(**course_data)
        assert course.title == "Test Course"
        assert course.price == 99.99
        assert course.status == CourseStatus.DRAFT

    @pytest.mark.backend
    def test_course_create_invalid_price(self):
        """Test CourseCreate with negative price"""
        from beanie import PydanticObjectId
        
        course_data = {
            "title": "Test Course",
            "description": "A test course description",
            "instructor_id": PydanticObjectId(),
            "price": -10.0
        }
        with pytest.raises(ValidationError):
            CourseCreate(**course_data)

    @pytest.mark.backend
    def test_course_update_partial_data(self):
        """Test CourseUpdate with partial data"""
        update_data = {
            "title": "Updated Course",
            "status": CourseStatus.PUBLISHED
        }
        course_update = CourseUpdate(**update_data)
        assert course_update.title == "Updated Course"
        assert course_update.status == CourseStatus.PUBLISHED
        assert course_update.description is None


class TestEnrollmentEntity:
    """Test Enrollment entity models"""

    @pytest.mark.backend
    def test_enrollment_create_valid_data(self):
        """Test EnrollmentCreate with valid data"""
        from beanie import PydanticObjectId
        
        enrollment_data = {
            "user_id": PydanticObjectId(),
            "course_id": PydanticObjectId(),
            "status": EnrollmentStatus.ACTIVE,
            "progress": 25.5
        }
        enrollment = EnrollmentCreate(**enrollment_data)
        assert enrollment.status == EnrollmentStatus.ACTIVE
        assert enrollment.progress == 25.5

    @pytest.mark.backend
    def test_enrollment_create_invalid_progress(self):
        """Test EnrollmentCreate with invalid progress"""
        from beanie import PydanticObjectId
        
        enrollment_data = {
            "user_id": PydanticObjectId(),
            "course_id": PydanticObjectId(),
            "progress": 150.0  # Invalid: > 100
        }
        with pytest.raises(ValidationError):
            EnrollmentCreate(**enrollment_data)

    @pytest.mark.backend
    def test_enrollment_update_partial_data(self):
        """Test EnrollmentUpdate with partial data"""
        update_data = {
            "status": EnrollmentStatus.COMPLETED,
            "progress": 100.0
        }
        enrollment_update = EnrollmentUpdate(**update_data)
        assert enrollment_update.status == EnrollmentStatus.COMPLETED
        assert enrollment_update.progress == 100.0
