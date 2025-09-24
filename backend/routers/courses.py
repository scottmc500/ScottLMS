"""
Course API routes
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId

from entities.courses import Course, CourseCreate, CourseUpdate, CourseResponse
from entities.users import User
from logs import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(course_data: CourseCreate):
    """Create a new course"""
    try:
        # Verify instructor exists
        instructor = await User.get(course_data.instructor_id)
        if not instructor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Instructor not found"
            )

        course = Course(**course_data.model_dump())
        await course.save()

        logger.info(f"Created course: {course.title}")
        course_dict = course.model_dump()
        # Handle both _id and id cases
        if "_id" in course_dict:
            course_dict["id"] = course_dict.pop("_id")
        elif "id" not in course_dict:
            # If neither _id nor id exists, use the course.id property
            course_dict["id"] = course.id
        return CourseResponse(**course_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating course: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create course",
        )


@router.get("/", response_model=List[CourseResponse])
async def get_courses():
    """Get all courses"""
    try:
        courses = await Course.find_all().to_list()
        result = []
        for course in courses:
            course_dict = course.model_dump()
            # Handle both _id and id cases
            if "_id" in course_dict:
                course_dict["id"] = course_dict.pop("_id")
            elif "id" not in course_dict:
                # If neither _id nor id exists, use the course.id property
                course_dict["id"] = course.id
            result.append(CourseResponse(**course_dict))
        return result
    except Exception as e:
        logger.error(f"Error fetching courses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch courses",
        )


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: PydanticObjectId):
    """Get a specific course by ID"""
    try:
        course = await Course.get(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
            )
        course_dict = course.model_dump()
        # Handle both _id and id cases
        if "_id" in course_dict:
            course_dict["id"] = course_dict.pop("_id")
        elif "id" not in course_dict:
            # If neither _id nor id exists, use the course.id property
            course_dict["id"] = course.id
        return CourseResponse(**course_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching course {course_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch course",
        )


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(course_id: PydanticObjectId, course_data: CourseUpdate):
    """Update a course"""
    try:
        course = await Course.get(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
            )

        # Update fields
        update_data = course_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)

        await course.save()
        logger.info(f"Updated course: {course.title}")
        course_dict = course.model_dump()
        # Handle both _id and id cases
        if "_id" in course_dict:
            course_dict["id"] = course_dict.pop("_id")
        elif "id" not in course_dict:
            # If neither _id nor id exists, use the course.id property
            course_dict["id"] = course.id
        return CourseResponse(**course_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating course {course_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update course",
        )


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: PydanticObjectId):
    """Delete a course"""
    try:
        course = await Course.get(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
            )

        await course.delete()
        logger.info(f"Deleted course: {course.title}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting course {course_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete course",
        )


@router.get("/instructor/{instructor_id}", response_model=List[CourseResponse])
async def get_courses_by_instructor(instructor_id: PydanticObjectId):
    """Get all courses by a specific instructor"""
    try:
        courses = await Course.find(Course.instructor_id == instructor_id).to_list()
        result = []
        for course in courses:
            course_dict = course.model_dump()
            # Handle both _id and id cases
            if "_id" in course_dict:
                course_dict["id"] = course_dict.pop("_id")
            elif "id" not in course_dict:
                # If neither _id nor id exists, use the course.id property
                course_dict["id"] = course.id
            result.append(CourseResponse(**course_dict))
        return result
    except Exception as e:
        logger.error(f"Error fetching courses for instructor {instructor_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch instructor courses",
        )
