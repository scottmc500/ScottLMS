"""
Enrollment endpoints for ScottLMS
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from beanie import PydanticObjectId

from models.enrollment import Enrollment, EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse, EnrollmentWithDetails, EnrollmentStatus
from core.exceptions import EnrollmentNotFoundError, DuplicateEnrollmentError
from services.enrollment_service import EnrollmentService

router = APIRouter()


@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment(enrollment_data: EnrollmentCreate):
    """Create a new enrollment"""
    try:
        enrollment = await EnrollmentService.create_enrollment(enrollment_data)
        return enrollment
    except DuplicateEnrollmentError:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[EnrollmentResponse])
async def get_enrollments(
    skip: int = Query(0, ge=0, description="Number of enrollments to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of enrollments to return"),
    status: Optional[EnrollmentStatus] = Query(None, description="Filter by enrollment status"),
    student_id: Optional[str] = Query(None, description="Filter by student ID"),
    course_id: Optional[str] = Query(None, description="Filter by course ID")
):
    """Get list of enrollments with optional filtering"""
    enrollments = await EnrollmentService.get_enrollments(
        skip=skip, 
        limit=limit, 
        status=status, 
        student_id=student_id,
        course_id=course_id
    )
    return enrollments


@router.get("/{enrollment_id}", response_model=EnrollmentWithDetails)
async def get_enrollment(enrollment_id: PydanticObjectId):
    """Get a specific enrollment by ID with student and course details"""
    enrollment = await EnrollmentService.get_enrollment_with_details(enrollment_id)
    if not enrollment:
        raise EnrollmentNotFoundError(str(enrollment_id))
    return enrollment


@router.put("/{enrollment_id}", response_model=EnrollmentResponse)
async def update_enrollment(enrollment_id: PydanticObjectId, enrollment_data: EnrollmentUpdate):
    """Update an enrollment"""
    enrollment = await EnrollmentService.update_enrollment(enrollment_id, enrollment_data)
    if not enrollment:
        raise EnrollmentNotFoundError(str(enrollment_id))
    return enrollment


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(enrollment_id: PydanticObjectId):
    """Delete an enrollment"""
    success = await EnrollmentService.delete_enrollment(enrollment_id)
    if not success:
        raise EnrollmentNotFoundError(str(enrollment_id))


@router.get("/student/{student_id}/courses", response_model=List[dict])
async def get_student_courses(student_id: PydanticObjectId):
    """Get all courses for a specific student"""
    courses = await EnrollmentService.get_student_courses(student_id)
    return courses


@router.get("/course/{course_id}/students", response_model=List[dict])
async def get_course_students(course_id: PydanticObjectId):
    """Get all students for a specific course"""
    students = await EnrollmentService.get_course_students(course_id)
    return students
