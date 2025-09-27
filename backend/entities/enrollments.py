"""
Enrollment entity for ScottLMS
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, ConfigDict


class EnrollmentStatus(str, Enum):
    """Enrollment status options"""

    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    SUSPENDED = "suspended"


class EnrollmentBase(BaseModel):
    """Base enrollment model"""

    user_id: PydanticObjectId = Field(..., description="Student ID")
    course_id: PydanticObjectId = Field(..., description="Course ID")
    status: EnrollmentStatus = Field(
        default=EnrollmentStatus.ACTIVE, description="Enrollment status"
    )
    progress: float = Field(
        default=0.0, ge=0, le=100, description="Course completion percentage"
    )


class EnrollmentCreate(EnrollmentBase):
    """Enrollment creation model"""

    pass


class EnrollmentUpdate(BaseModel):
    """Enrollment update model"""

    status: Optional[EnrollmentStatus] = None
    progress: Optional[float] = Field(
        None, ge=0, le=100, description="Course completion percentage"
    )


class Enrollment(EnrollmentBase, Document):
    """Enrollment document model for MongoDB"""

    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None

    class Settings:
        name = "enrollments"


class EnrollmentResponse(EnrollmentBase):
    """Enrollment response model"""

    id: PydanticObjectId
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
