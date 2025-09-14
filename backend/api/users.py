"""
User endpoints for ScottLMS
"""

from typing import List, Optional

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.exceptions import UserNotFoundError
from models.user import User, UserCreate, UserResponse, UserRole, UserUpdate
from services.user_service import UserService

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    try:
        user = await UserService.create_user(user_data)
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
):
    """Get list of users with optional filtering"""
    users = await UserService.get_users(
        skip=skip, limit=limit, role=role, is_active=is_active
    )
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: PydanticObjectId):
    """Get a specific user by ID"""
    user = await UserService.get_user_by_id(user_id)
    if not user:
        raise UserNotFoundError(str(user_id))
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: PydanticObjectId, user_data: UserUpdate):
    """Update a user"""
    user = await UserService.update_user(user_id, user_data)
    if not user:
        raise UserNotFoundError(str(user_id))
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: PydanticObjectId):
    """Delete a user"""
    success = await UserService.delete_user(user_id)
    if not success:
        raise UserNotFoundError(str(user_id))


@router.get("/{user_id}/courses", response_model=List[dict])
async def get_user_courses(user_id: PydanticObjectId):
    """Get courses for a specific user (as student or instructor)"""
    courses = await UserService.get_user_courses(user_id)
    return courses
