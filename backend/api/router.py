"""
API router configuration
"""

from fastapi import APIRouter

from api import courses, enrollments, users

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(
    enrollments.router, prefix="/enrollments", tags=["enrollments"]
)
