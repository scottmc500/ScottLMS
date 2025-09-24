"""
Enrollment API routes
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId

from entities.enrollments import (
    Enrollment,
    EnrollmentCreate,
    EnrollmentUpdate,
    EnrollmentResponse,
)
from entities.users import User
from entities.courses import Course
from logs import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED
)
async def create_enrollment(enrollment_data: EnrollmentCreate):
    """Create a new enrollment"""
    try:
        # Verify user and course exist
        user = await User.get(enrollment_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
            )

        course = await Course.get(enrollment_data.course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Course not found"
            )

        # Check if already enrolled
        existing_enrollment = await Enrollment.find_one(
            Enrollment.user_id == enrollment_data.user_id,
            Enrollment.course_id == enrollment_data.course_id,
        )
        if existing_enrollment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already enrolled in this course",
            )

        enrollment = Enrollment(**enrollment_data.dict())
        await enrollment.save()

        # Update course enrollment count
        course.enrollment_count += 1
        await course.save()

        logger.info(
            f"Created enrollment: User {enrollment.user_id} in Course {enrollment.course_id}"
        )
        enrollment_dict = enrollment.dict()
        # Handle both _id and id cases
        if "_id" in enrollment_dict:
            enrollment_dict["id"] = enrollment_dict.pop("_id")
        elif "id" not in enrollment_dict:
            # If neither _id nor id exists, use the enrollment.id property
            enrollment_dict["id"] = enrollment.id
        return EnrollmentResponse(**enrollment_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating enrollment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create enrollment",
        )


@router.get("/", response_model=List[EnrollmentResponse])
async def get_enrollments():
    """Get all enrollments"""
    try:
        enrollments = await Enrollment.find_all().to_list()
        result = []
        for enrollment in enrollments:
            enrollment_dict = enrollment.dict()
            # Handle both _id and id cases
            if "_id" in enrollment_dict:
                enrollment_dict["id"] = enrollment_dict.pop("_id")
            elif "id" not in enrollment_dict:
                # If neither _id nor id exists, use the enrollment.id property
                enrollment_dict["id"] = enrollment.id
            result.append(EnrollmentResponse(**enrollment_dict))
        return result
    except Exception as e:
        logger.error(f"Error fetching enrollments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch enrollments",
        )


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
async def get_enrollment(enrollment_id: PydanticObjectId):
    """Get a specific enrollment by ID"""
    try:
        enrollment = await Enrollment.get(enrollment_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
            )
        enrollment_dict = enrollment.dict()
        # Handle both _id and id cases
        if "_id" in enrollment_dict:
            enrollment_dict["id"] = enrollment_dict.pop("_id")
        elif "id" not in enrollment_dict:
            # If neither _id nor id exists, use the enrollment.id property
            enrollment_dict["id"] = enrollment.id
        return EnrollmentResponse(**enrollment_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching enrollment {enrollment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch enrollment",
        )


@router.put("/{enrollment_id}", response_model=EnrollmentResponse)
async def update_enrollment(
    enrollment_id: PydanticObjectId, enrollment_data: EnrollmentUpdate
):
    """Update an enrollment"""
    try:
        enrollment = await Enrollment.get(enrollment_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
            )

        # Update only provided fields
        update_data = enrollment_data.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(enrollment, field, value)

        await enrollment.save()

        logger.info(f"Updated enrollment: {enrollment_id}")
        enrollment_dict = enrollment.dict()
        # Handle both _id and id cases
        if "_id" in enrollment_dict:
            enrollment_dict["id"] = enrollment_dict.pop("_id")
        elif "id" not in enrollment_dict:
            # If neither _id nor id exists, use the enrollment.id property
            enrollment_dict["id"] = enrollment.id
        return EnrollmentResponse(**enrollment_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating enrollment {enrollment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update enrollment",
        )


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(enrollment_id: PydanticObjectId):
    """Delete an enrollment"""
    try:
        enrollment = await Enrollment.get(enrollment_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
            )

        # Update course enrollment count
        course = await Course.get(enrollment.course_id)
        if course:
            course.enrollment_count = max(0, course.enrollment_count - 1)
            await course.save()

        await enrollment.delete()
        logger.info(f"Deleted enrollment: {enrollment_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting enrollment {enrollment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete enrollment",
        )


@router.get("/user/{user_id}", response_model=List[EnrollmentResponse])
async def get_user_enrollments(user_id: PydanticObjectId):
    """Get all enrollments for a specific user"""
    try:
        enrollments = await Enrollment.find(Enrollment.user_id == user_id).to_list()
        result = []
        for enrollment in enrollments:
            enrollment_dict = enrollment.dict()
            # Handle both _id and id cases
            if "_id" in enrollment_dict:
                enrollment_dict["id"] = enrollment_dict.pop("_id")
            elif "id" not in enrollment_dict:
                # If neither _id nor id exists, use the enrollment.id property
                enrollment_dict["id"] = enrollment.id
            result.append(EnrollmentResponse(**enrollment_dict))
        return result
    except Exception as e:
        logger.error(f"Error fetching enrollments for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user enrollments",
        )


@router.get("/course/{course_id}", response_model=List[EnrollmentResponse])
async def get_course_enrollments(course_id: PydanticObjectId):
    """Get all enrollments for a specific course"""
    try:
        enrollments = await Enrollment.find(Enrollment.course_id == course_id).to_list()
        result = []
        for enrollment in enrollments:
            enrollment_dict = enrollment.dict()
            # Handle both _id and id cases
            if "_id" in enrollment_dict:
                enrollment_dict["id"] = enrollment_dict.pop("_id")
            elif "id" not in enrollment_dict:
                # If neither _id nor id exists, use the enrollment.id property
                enrollment_dict["id"] = enrollment.id
            result.append(EnrollmentResponse(**enrollment_dict))
        return result
    except Exception as e:
        logger.error(f"Error fetching enrollments for course {course_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch course enrollments",
        )
