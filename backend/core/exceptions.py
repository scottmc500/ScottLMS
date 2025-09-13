"""
Custom exceptions for ScottLMS
"""

from fastapi import HTTPException, status


class ScottLMSException(HTTPException):
    """Base exception for ScottLMS"""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.detail = detail
        self.status_code = status_code
        super().__init__(status_code=status_code, detail=detail)


class UserNotFoundError(ScottLMSException):
    """User not found exception"""
    
    def __init__(self, user_id: str):
        super().__init__(
            detail=f"User with ID {user_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class CourseNotFoundError(ScottLMSException):
    """Course not found exception"""
    
    def __init__(self, course_id: str):
        super().__init__(
            detail=f"Course with ID {course_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class EnrollmentNotFoundError(ScottLMSException):
    """Enrollment not found exception"""
    
    def __init__(self, enrollment_id: str):
        super().__init__(
            detail=f"Enrollment with ID {enrollment_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class DuplicateEnrollmentError(ScottLMSException):
    """Duplicate enrollment exception"""
    
    def __init__(self, user_id: str, course_id: str):
        super().__init__(
            detail=f"User {user_id} is already enrolled in course {course_id}",
            status_code=status.HTTP_409_CONFLICT
        )


class InvalidCredentialsError(ScottLMSException):
    """Invalid credentials exception"""
    
    def __init__(self):
        super().__init__(
            detail="Invalid email or password",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class InsufficientPermissionsError(ScottLMSException):
    """Insufficient permissions exception"""
    
    def __init__(self, required_role: str):
        super().__init__(
            detail=f"Insufficient permissions. Required role: {required_role}",
            status_code=status.HTTP_403_FORBIDDEN
        )
