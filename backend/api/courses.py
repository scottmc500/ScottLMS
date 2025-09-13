"""
Course endpoints for ScottLMS
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from beanie import PydanticObjectId

from models.course import Course, CourseCreate, CourseUpdate, CourseResponse, CourseWithInstructor, CourseStatus
from core.exceptions import CourseNotFoundError
from services.course_service import CourseService

router = APIRouter()


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(course_data: CourseCreate):
    """Create a new course"""
    try:
        course = await CourseService.create_course(course_data)
        return course
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[CourseResponse])
async def get_courses(
    skip: int = Query(0, ge=0, description="Number of courses to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of courses to return"),
    status: Optional[CourseStatus] = Query(None, description="Filter by course status"),
    instructor_id: Optional[str] = Query(None, description="Filter by instructor ID"),
    search: Optional[str] = Query(None, description="Search in title and description")
):
    """Get list of courses with optional filtering and search"""
    courses = await CourseService.get_courses(
        skip=skip, 
        limit=limit, 
        status=status, 
        instructor_id=instructor_id,
        search=search
    )
    return courses


@router.get("/{course_id}", response_model=CourseWithInstructor)
async def get_course(course_id: PydanticObjectId):
    """Get a specific course by ID with instructor details"""
    course = await CourseService.get_course_with_instructor(course_id)
    if not course:
        raise CourseNotFoundError(str(course_id))
    return course


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(course_id: PydanticObjectId, course_data: CourseUpdate):
    """Update a course"""
    course = await CourseService.update_course(course_id, course_data)
    if not course:
        raise CourseNotFoundError(str(course_id))
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: PydanticObjectId):
    """Delete a course"""
    success = await CourseService.delete_course(course_id)
    if not success:
        raise CourseNotFoundError(str(course_id))


@router.get("/{course_id}/enrollments", response_model=List[dict])
async def get_course_enrollments(course_id: PydanticObjectId):
    """Get enrollments for a specific course"""
    enrollments = await CourseService.get_course_enrollments(course_id)
    return enrollments


@router.get("/{course_id}/students", response_model=List[dict])
async def get_course_students(course_id: PydanticObjectId):
    """Get students enrolled in a specific course"""
    students = await CourseService.get_course_students(course_id)
    return students
