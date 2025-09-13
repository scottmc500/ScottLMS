"""
Course service for ScottLMS
"""

from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId
import structlog

from models.course import Course, CourseCreate, CourseUpdate, CourseResponse, CourseWithInstructor, CourseStatus
from models.user import User
from core.exceptions import CourseNotFoundError

logger = structlog.get_logger()


class CourseService:
    """Service class for course operations"""
    
    @staticmethod
    async def create_course(course_data: CourseCreate) -> CourseResponse:
        """Create a new course"""
        try:
            # Verify instructor exists
            instructor = await User.get(PydanticObjectId(course_data.instructor_id))
            if not instructor:
                raise ValueError("Instructor not found")
            
            if instructor.role != "instructor" and instructor.role != "admin":
                raise ValueError("User is not authorized to create courses")
            
            # Create course document
            course_dict = course_data.dict()
            course = Course(**course_dict)
            await course.insert()
            
            logger.info("Course created successfully", course_id=str(course.id), title=course.title)
            return CourseResponse.model_validate(course)
            
        except Exception as e:
            logger.error("Failed to create course", error=str(e))
            raise
    
    @staticmethod
    async def get_course_by_id(course_id: PydanticObjectId) -> Optional[CourseResponse]:
        """Get course by ID"""
        course = await Course.get(course_id)
        if course:
            return CourseResponse.model_validate(course)
        return None
    
    @staticmethod
    async def get_course_with_instructor(course_id: PydanticObjectId) -> Optional[CourseWithInstructor]:
        """Get course by ID with instructor details"""
        course = await Course.get(course_id)
        if not course:
            return None
        
        # Get instructor details
        instructor = await User.get(PydanticObjectId(course.instructor_id))
        instructor_data = None
        if instructor:
            instructor_data = {
                "id": str(instructor.id),
                "username": instructor.username,
                "first_name": instructor.first_name,
                "last_name": instructor.last_name,
                "email": instructor.email
            }
        
        course_dict = course.dict()
        course_dict["instructor"] = instructor_data
        
        return CourseWithInstructor(**course_dict)
    
    @staticmethod
    async def get_courses(
        skip: int = 0, 
        limit: int = 100, 
        status: Optional[CourseStatus] = None, 
        instructor_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[CourseResponse]:
        """Get list of courses with filtering and search"""
        query = {}
        
        if status:
            query["status"] = status
        if instructor_id:
            query["instructor_id"] = instructor_id
        
        if search:
            # Use MongoDB text search
            courses = await Course.find({"$text": {"$search": search}}, query).skip(skip).limit(limit).to_list()
        else:
            courses = await Course.find(query).skip(skip).limit(limit).to_list()
        
        return [CourseResponse.model_validate(course) for course in courses]
    
    @staticmethod
    async def update_course(course_id: PydanticObjectId, course_data: CourseUpdate) -> Optional[CourseResponse]:
        """Update course"""
        course = await Course.get(course_id)
        if not course:
            return None
        
        # Update fields
        update_data = course_data.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await course.update({"$set": update_data})
            # Reload the course from database to get updated data
            course = await Course.get(course_id)
        
        logger.info("Course updated successfully", course_id=str(course_id))
        return CourseResponse.model_validate(course)
    
    @staticmethod
    async def delete_course(course_id: PydanticObjectId) -> bool:
        """Delete course"""
        course = await Course.get(course_id)
        if not course:
            return False
        
        await course.delete()
        logger.info("Course deleted successfully", course_id=str(course_id))
        return True
    
    @staticmethod
    async def get_course_enrollments(course_id: PydanticObjectId) -> List[dict]:
        """Get enrollments for a specific course"""
        # This would typically involve joining with enrollments
        # For now, return empty list - will be implemented when we add more complex queries
        return []
    
    @staticmethod
    async def get_course_students(course_id: PydanticObjectId) -> List[dict]:
        """Get students enrolled in a specific course"""
        # This would typically involve joining with enrollments and users
        # For now, return empty list - will be implemented when we add more complex queries
        return []
