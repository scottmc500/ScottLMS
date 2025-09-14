"""
Tests for data models
"""

import pytest
from pydantic import ValidationError
from backend.models.user import User, UserCreate, UserUpdate, UserRole
from backend.models.course import Course, CourseCreate, CourseUpdate, CourseStatus
from backend.models.enrollment import Enrollment, EnrollmentCreate, EnrollmentUpdate, EnrollmentStatus


class TestUserModel:
    """Test user model validation"""
    
    @pytest.mark.backend
    def test_user_create_valid(self):
        """Test valid user creation"""
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            role=UserRole.STUDENT,
            password="password123"
        )
        assert user_data.email == "test@example.com"
        assert user_data.username == "testuser"
        assert user_data.role == UserRole.STUDENT
    
    @pytest.mark.backend
    def test_user_create_invalid_email(self):
        """Test invalid email validation"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="invalid-email",
                username="testuser",
                first_name="Test",
                last_name="User",
                role=UserRole.STUDENT,
                password="password123"
            )
    
    @pytest.mark.backend
    def test_user_create_short_password(self):
        """Test password length validation"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                username="testuser",
                first_name="Test",
                last_name="User",
                role=UserRole.STUDENT,
                password="123"
            )
    
    @pytest.mark.backend
    def test_user_update_partial(self):
        """Test partial user update"""
        user_update = UserUpdate(first_name="Updated")
        assert user_update.first_name == "Updated"
        assert user_update.last_name is None


class TestCourseModel:
    """Test course model validation"""
    
    @pytest.mark.backend
    def test_course_create_valid(self):
        """Test valid course creation"""
        course_data = CourseCreate(
            title="Test Course",
            description="A test course",
            instructor_id="507f1f77bcf86cd799439011"
        )
        assert course_data.title == "Test Course"
        assert course_data.status == CourseStatus.DRAFT
    
    @pytest.mark.backend
    def test_course_create_empty_title(self):
        """Test empty title validation"""
        with pytest.raises(ValidationError):
            CourseCreate(
                title="",
                description="A test course",
                instructor_id="507f1f77bcf86cd799439011"
            )
    
    @pytest.mark.backend
    def test_course_update_partial(self):
        """Test partial course update"""
        course_update = CourseUpdate(title="Updated Title")
        assert course_update.title == "Updated Title"
        assert course_update.description is None


class TestEnrollmentModel:
    """Test enrollment model validation"""
    
    @pytest.mark.backend
    def test_enrollment_create_valid(self):
        """Test valid enrollment creation"""
        from bson import ObjectId
        student_id = ObjectId("507f1f77bcf86cd799439011")
        course_id = ObjectId("507f1f77bcf86cd799439012")
        
        enrollment_data = EnrollmentCreate(
            student_id=str(student_id),
            course_id=str(course_id)
        )
        assert enrollment_data.student_id == student_id
        assert enrollment_data.course_id == course_id
        assert enrollment_data.status == EnrollmentStatus.ACTIVE
    
    @pytest.mark.backend
    def test_enrollment_progress_validation(self):
        """Test progress percentage validation"""
        # Valid progress
        enrollment = EnrollmentUpdate(progress_percentage=50.0)
        assert enrollment.progress_percentage == 50.0
        
        # Invalid progress (negative)
        with pytest.raises(ValidationError):
            EnrollmentUpdate(progress_percentage=-10.0)
        
        # Invalid progress (over 100)
        with pytest.raises(ValidationError):
            EnrollmentUpdate(progress_percentage=150.0)
