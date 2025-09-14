"""
User service for ScottLMS
"""

from datetime import datetime
from typing import List, Optional

import structlog
from beanie import PydanticObjectId
from passlib.context import CryptContext

from core.exceptions import UserNotFoundError
from models.user import User, UserCreate, UserResponse, UserRole, UserUpdate

logger = structlog.get_logger()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service class for user operations"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    async def create_user(user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = await User.find_one(User.email == user_data.email)
            if existing_user:
                raise ValueError("User with this email already exists")

            existing_username = await User.find_one(User.username == user_data.username)
            if existing_username:
                raise ValueError("User with this username already exists")

            # Hash password
            hashed_password = UserService.get_password_hash(user_data.password)

            # Create user document
            user_dict = user_data.dict()
            user_dict.pop("password")  # Remove plain password
            user_dict["hashed_password"] = hashed_password

            user = User(**user_dict)
            await user.insert()

            logger.info(
                "User created successfully", user_id=str(user.id), email=user.email
            )
            return UserResponse.model_validate(user)

        except Exception as e:
            logger.error("Failed to create user", error=str(e))
            raise

    @staticmethod
    async def get_user_by_id(user_id: PydanticObjectId) -> Optional[UserResponse]:
        """Get user by ID"""
        user = await User.get(user_id)
        if user:
            return UserResponse.model_validate(user)
        return None

    @staticmethod
    async def get_users(
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
    ) -> List[UserResponse]:
        """Get list of users with filtering"""
        query = {}

        if role:
            query["role"] = role
        if is_active is not None:
            query["is_active"] = is_active

        users = await User.find(query).skip(skip).limit(limit).to_list()
        return [UserResponse.model_validate(user) for user in users]

    @staticmethod
    async def update_user(
        user_id: PydanticObjectId, user_data: UserUpdate
    ) -> Optional[UserResponse]:
        """Update user"""
        user = await User.get(user_id)
        if not user:
            return None

        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await user.update({"$set": update_data})
            # Reload the user from database to get updated data
            user = await User.get(user_id)

        logger.info("User updated successfully", user_id=str(user_id))
        return UserResponse.model_validate(user)

    @staticmethod
    async def delete_user(user_id: PydanticObjectId) -> bool:
        """Delete user"""
        user = await User.get(user_id)
        if not user:
            return False

        await user.delete()
        logger.info("User deleted successfully", user_id=str(user_id))
        return True

    @staticmethod
    async def get_user_courses(user_id: PydanticObjectId) -> List[dict]:
        """Get courses for a user (as student or instructor)"""
        # This would typically involve joining with enrollments and courses
        # For now, return empty list - will be implemented when we add more complex queries
        return []
