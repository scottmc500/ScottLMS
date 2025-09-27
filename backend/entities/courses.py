"""
Course entity for ScottLMS
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, ConfigDict


class CourseStatus(str, Enum):
    """Course status options"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CourseBase(BaseModel):
    """Base course model"""

    title: str = Field(..., min_length=1, max_length=200, description="Course title")
    description: str = Field(
        ..., min_length=1, max_length=1000, description="Course description"
    )
    status: CourseStatus = Field(
        default=CourseStatus.DRAFT, description="Course status"
    )
    price: float = Field(default=0.0, ge=0, description="Course price")
    duration_hours: Optional[int] = Field(
        None, ge=1, description="Course duration in hours"
    )
    max_students: Optional[int] = Field(
        None, ge=1, description="Maximum number of students"
    )
    tags: List[str] = Field(default_factory=list, description="Course tags")


class CourseCreate(CourseBase):
    """Course creation model"""

    instructor_id: PydanticObjectId = Field(..., description="Instructor ID")


class CourseUpdate(BaseModel):
    """Course update model"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    status: Optional[CourseStatus] = None
    price: Optional[float] = Field(None, ge=0)
    duration_hours: Optional[int] = Field(None, ge=1)
    max_students: Optional[int] = Field(None, ge=1)
    tags: Optional[List[str]] = None


class Course(CourseBase, Document):
    """Course document model for MongoDB"""

    instructor_id: PydanticObjectId = Field(..., description="Instructor ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    enrollment_count: int = Field(default=0, description="Number of enrolled students")

    class Settings:
        name = "courses"


class CourseResponse(CourseBase):
    """Course response model"""

    id: PydanticObjectId
    instructor_id: PydanticObjectId
    created_at: datetime
    updated_at: datetime
    enrollment_count: int
