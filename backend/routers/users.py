"""
User API routes
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId
import hashlib

from entities.users import User, UserCreate, UserUpdate, UserResponse
from logs import get_logger

logger = get_logger(__name__)
router = APIRouter()


def hash_password(password: str) -> str:
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = await User.find_one(User.email == user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        # Create new user
        user_dict = user_data.model_dump()
        password = user_dict.pop("password")
        user_dict["hashed_password"] = hash_password(password)

        user = User(**user_dict)
        await user.save()

        logger.info(f"Created user: {user.email}")
        user_dict = user.model_dump()
        # Handle both _id and id cases
        if "_id" in user_dict:
            user_dict["id"] = user_dict.pop("_id")
        elif "id" not in user_dict:
            # If neither _id nor id exists, use the user.id property
            user_dict["id"] = user.id
        return UserResponse(**user_dict)

    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )


@router.get("/", response_model=List[UserResponse])
async def get_users():
    """Get all users"""
    try:
        users = await User.find_all().to_list()
        result = []
        for user in users:
            user_dict = user.model_dump()
            logger.debug(f"User dict keys: {list(user_dict.keys())}")
            # Handle both _id and id cases
            if "_id" in user_dict:
                user_dict["id"] = user_dict.pop("_id")
            elif "id" not in user_dict:
                # If neither _id nor id exists, use the user.id property
                user_dict["id"] = user.id
            result.append(UserResponse(**user_dict))
        return result
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users",
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: PydanticObjectId):
    """Get a specific user by ID"""
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        user_dict = user.model_dump()
        # Handle both _id and id cases
        if "_id" in user_dict:
            user_dict["id"] = user_dict.pop("_id")
        elif "id" not in user_dict:
            # If neither _id nor id exists, use the user.id property
            user_dict["id"] = user.id
        return UserResponse(**user_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user",
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: PydanticObjectId, user_data: UserUpdate):
    """Update a user"""
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await user.save()
        logger.info(f"Updated user: {user.email}")
        user_dict = user.model_dump()
        # Handle both _id and id cases
        if "_id" in user_dict:
            user_dict["id"] = user_dict.pop("_id")
        elif "id" not in user_dict:
            # If neither _id nor id exists, use the user.id property
            user_dict["id"] = user.id
        return UserResponse(**user_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: PydanticObjectId):
    """Delete a user"""
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        await user.delete()
        logger.info(f"Deleted user: {user.email}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        )
