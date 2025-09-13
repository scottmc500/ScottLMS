"""
Enrollment model for ScottLMS
"""

from datetime import datetime
from typing import Optional
from beanie import Document, PydanticObjectId, Link
from pydantic import BaseModel, Field
from enum import Enum

from models.user import User
from models.course import Course


class EnrollmentStatus(str, Enum):
    """Enrollment status options"""
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    SUSPENDED = "suspended"


class EnrollmentBase(BaseModel):
    """Base enrollment model"""
    status: EnrollmentStatus = Field(default=EnrollmentStatus.ACTIVE, description="Enrollment status")
    progress_percentage: float = Field(default=0.0, ge=0, le=100, description="Course progress percentage")
    grade: Optional[float] = Field(None, ge=0, le=100, description="Final grade")
    notes: Optional[str] = Field(None, max_length=1000, description="Enrollment notes")


class EnrollmentCreate(EnrollmentBase):
    """Enrollment creation model"""
    student_id: PydanticObjectId = Field(..., description="Student ID")
    course_id: PydanticObjectId = Field(..., description="Course ID")


class EnrollmentUpdate(BaseModel):
    """Enrollment update model"""
    status: Optional[EnrollmentStatus] = None
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    grade: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = Field(None, max_length=1000)


class EnrollmentInDB(EnrollmentBase):
    """Enrollment model for database storage"""
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    student_id: PydanticObjectId = Field(..., description="Student ID")
    course_id: PydanticObjectId = Field(..., description="Course ID")
    enrollment_date: datetime = Field(default_factory=datetime.utcnow, description="Enrollment date")
    completion_date: Optional[datetime] = Field(None, description="Course completion date")
    last_accessed: Optional[datetime] = Field(None, description="Last time student accessed the course")

    class Config:
        populate_by_name = True


class Enrollment(EnrollmentInDB, Document):
    """Enrollment document model for MongoDB"""
    
    class Settings:
        name = "enrollments"


class EnrollmentResponse(EnrollmentBase):
    """Enrollment response model"""
    id: PydanticObjectId
    student_id: PydanticObjectId
    course_id: PydanticObjectId
    enrollment_date: datetime
    completion_date: Optional[datetime] = None
    last_accessed: Optional[datetime] = None

    class Config:
        from_attributes = True


class EnrollmentWithDetails(EnrollmentResponse):
    """Enrollment response model with student and course details"""
    student: Optional[dict] = None  # Will be populated with student details
    course: Optional[dict] = None   # Will be populated with course details
