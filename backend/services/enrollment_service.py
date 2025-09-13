"""
Enrollment service for ScottLMS
"""

from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId
import structlog

from models.enrollment import Enrollment, EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse, EnrollmentWithDetails, EnrollmentStatus
from models.user import User
from models.course import Course
from core.exceptions import EnrollmentNotFoundError, DuplicateEnrollmentError

logger = structlog.get_logger()


class EnrollmentService:
    """Service class for enrollment operations"""
    
    @staticmethod
    async def create_enrollment(enrollment_data: EnrollmentCreate) -> EnrollmentResponse:
        """Create a new enrollment"""
        try:
            # Verify student exists
            student = await User.get(PydanticObjectId(enrollment_data.student_id))
            if not student:
                raise ValueError("Student not found")
            
            if student.role != "student":
                raise ValueError("User is not a student")
            
            # Verify course exists
            course = await Course.get(PydanticObjectId(enrollment_data.course_id))
            if not course:
                raise ValueError("Course not found")
            
            if course.status != "published":
                raise ValueError("Course is not available for enrollment")
            
            # Check if enrollment already exists
            existing_enrollment = await Enrollment.find_one(
                Enrollment.student_id == enrollment_data.student_id,
                Enrollment.course_id == enrollment_data.course_id
            )
            if existing_enrollment:
                raise DuplicateEnrollmentError(enrollment_data.student_id, enrollment_data.course_id)
            
            # Create enrollment document
            enrollment_dict = enrollment_data.dict()
            enrollment = Enrollment(**enrollment_dict)
            await enrollment.insert()
            
            # Update course enrollment count
            await course.update({"$inc": {"enrollment_count": 1}})
            
            logger.info("Enrollment created successfully", enrollment_id=str(enrollment.id))
            return EnrollmentResponse.model_validate(enrollment)
            
        except DuplicateEnrollmentError:
            raise
        except Exception as e:
            logger.error("Failed to create enrollment", error=str(e))
            raise
    
    @staticmethod
    async def get_enrollment_by_id(enrollment_id: PydanticObjectId) -> Optional[EnrollmentResponse]:
        """Get enrollment by ID"""
        enrollment = await Enrollment.get(enrollment_id)
        if enrollment:
            return EnrollmentResponse.model_validate(enrollment)
        return None
    
    @staticmethod
    async def get_enrollment_with_details(enrollment_id: PydanticObjectId) -> Optional[EnrollmentWithDetails]:
        """Get enrollment by ID with student and course details"""
        enrollment = await Enrollment.get(enrollment_id)
        if not enrollment:
            return None
        
        # Get student details
        student = await User.get(PydanticObjectId(enrollment.student_id))
        student_data = None
        if student:
            student_data = {
                "id": str(student.id),
                "username": student.username,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email
            }
        
        # Get course details
        course = await Course.get(PydanticObjectId(enrollment.course_id))
        course_data = None
        if course:
            course_data = {
                "id": str(course.id),
                "title": course.title,
                "description": course.description,
                "status": course.status
            }
        
        enrollment_dict = enrollment.dict()
        enrollment_dict["student"] = student_data
        enrollment_dict["course"] = course_data
        
        return EnrollmentWithDetails(**enrollment_dict)
    
    @staticmethod
    async def get_enrollments(
        skip: int = 0, 
        limit: int = 100, 
        status: Optional[EnrollmentStatus] = None, 
        student_id: Optional[str] = None,
        course_id: Optional[str] = None
    ) -> List[EnrollmentResponse]:
        """Get list of enrollments with filtering"""
        query = {}
        
        if status:
            query["status"] = status
        if student_id:
            query["student_id"] = student_id
        if course_id:
            query["course_id"] = course_id
        
        enrollments = await Enrollment.find(query).skip(skip).limit(limit).to_list()
        return [EnrollmentResponse.model_validate(enrollment) for enrollment in enrollments]
    
    @staticmethod
    async def update_enrollment(enrollment_id: PydanticObjectId, enrollment_data: EnrollmentUpdate) -> Optional[EnrollmentResponse]:
        """Update enrollment"""
        enrollment = await Enrollment.get(enrollment_id)
        if not enrollment:
            return None
        
        # Update fields
        update_data = enrollment_data.dict(exclude_unset=True)
        if update_data:
            # Update last_accessed if progress is being updated
            if "progress_percentage" in update_data:
                update_data["last_accessed"] = datetime.utcnow()
            
            # Set completion_date if status is being changed to completed
            if update_data.get("status") == "completed":
                update_data["completion_date"] = datetime.utcnow()
            
            await enrollment.update({"$set": update_data})
            # Reload the enrollment from database to get updated data
            enrollment = await Enrollment.get(enrollment_id)
        
        logger.info("Enrollment updated successfully", enrollment_id=str(enrollment_id))
        return EnrollmentResponse.model_validate(enrollment)
    
    @staticmethod
    async def delete_enrollment(enrollment_id: PydanticObjectId) -> bool:
        """Delete enrollment"""
        enrollment = await Enrollment.get(enrollment_id)
        if not enrollment:
            return False
        
        # Update course enrollment count
        course = await Course.get(PydanticObjectId(enrollment.course_id))
        if course:
            await course.update({"$inc": {"enrollment_count": -1}})
        
        await enrollment.delete()
        logger.info("Enrollment deleted successfully", enrollment_id=str(enrollment_id))
        return True
    
    @staticmethod
    async def get_student_courses(student_id: PydanticObjectId) -> List[dict]:
        """Get all courses for a specific student"""
        # This would typically involve joining with courses
        # For now, return empty list - will be implemented when we add more complex queries
        return []
    
    @staticmethod
    async def get_course_students(course_id: PydanticObjectId) -> List[dict]:
        """Get all students for a specific course"""
        # This would typically involve joining with users
        # For now, return empty list - will be implemented when we add more complex queries
        return []
