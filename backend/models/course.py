"""
Course model for ScottLMS
"""

from datetime import datetime
from typing import Optional, List
from beanie import Document, PydanticObjectId, Link
from pydantic import BaseModel, Field
from enum import Enum

from models.user import User


class CourseStatus(str, Enum):
    """Course status options"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CourseBase(BaseModel):
    """Base course model"""
    title: str = Field(..., min_length=1, max_length=200, description="Course title")
    description: str = Field(..., min_length=1, max_length=1000, description="Course description")
    short_description: Optional[str] = Field(None, max_length=300, description="Short course description")
    status: CourseStatus = Field(default=CourseStatus.DRAFT, description="Course status")
    price: float = Field(default=0.0, ge=0, description="Course price")
    duration_hours: Optional[int] = Field(None, ge=1, description="Course duration in hours")
    max_students: Optional[int] = Field(None, ge=1, description="Maximum number of students")
    tags: List[str] = Field(default_factory=list, description="Course tags")
    thumbnail_url: Optional[str] = Field(None, description="Course thumbnail URL")
    prerequisites: List[str] = Field(default_factory=list, description="Course prerequisites")


class CourseCreate(CourseBase):
    """Course creation model"""
    instructor_id: PydanticObjectId = Field(..., description="Instructor ID")


class CourseUpdate(BaseModel):
    """Course update model"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    short_description: Optional[str] = Field(None, max_length=300)
    status: Optional[CourseStatus] = None
    price: Optional[float] = Field(None, ge=0)
    duration_hours: Optional[int] = Field(None, ge=1)
    max_students: Optional[int] = Field(None, ge=1)
    tags: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None
    prerequisites: Optional[List[str]] = None


class CourseInDB(CourseBase):
    """Course model for database storage"""
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    instructor_id: PydanticObjectId = Field(..., description="Instructor ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    enrollment_count: int = Field(default=0, description="Number of enrolled students")

    class Config:
        populate_by_name = True


class Course(CourseInDB, Document):
    """Course document model for MongoDB"""
    
    class Settings:
        name = "courses"


class CourseResponse(CourseBase):
    """Course response model"""
    id: PydanticObjectId
    instructor_id: PydanticObjectId
    created_at: datetime
    updated_at: datetime
    enrollment_count: int

    class Config:
        from_attributes = True


class CourseWithInstructor(CourseResponse):
    """Course response model with instructor information"""
    instructor: Optional[dict] = None  # Will be populated with instructor details
