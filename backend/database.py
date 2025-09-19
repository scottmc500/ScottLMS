"""
Database configuration and connection management
"""

import os
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from logs import get_logger

logger = get_logger(__name__)


# Database configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/scottlms")
DATABASE_NAME = os.getenv("DATABASE_NAME", "scottlms")

# Global database client
client: AsyncIOMotorClient = None


async def init_db() -> None:
    """Initialize database connection and collections"""
    global client
    
    try:
        # Import models here to avoid circular imports
        from entities.users import User
        from entities.courses import Course
        from entities.enrollments import Enrollment
        
        # Create MongoDB client
        client = AsyncIOMotorClient(MONGODB_URL)
        
        # Test connection
        await client.admin.command("ping")
        logger.info("Connected to MongoDB successfully")
        
        # Initialize Beanie with document models
        await init_beanie(
            database=client[DATABASE_NAME],
            document_models=[User, Course, Enrollment],
        )
        
        logger.info("Database collections initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


async def close_db() -> None:
    """Close database connection"""
    global client
    
    if client:
        client.close()
        logger.info("Database connection closed")


def get_database():
    """Get database instance"""
    return client[DATABASE_NAME]
