"""
Database configuration and connection management
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import structlog

from core.config import settings
from models.user import User
from models.course import Course
from models.enrollment import Enrollment

logger = structlog.get_logger()

# Global database client
client: AsyncIOMotorClient = None


async def init_db() -> None:
    """Initialize database connection and collections"""
    global client
    
    try:
        # Create MongoDB client
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        
        # Test connection
        await client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Initialize Beanie with document models
        await init_beanie(
            database=client[settings.DATABASE_NAME],
            document_models=[User, Course, Enrollment]
        )
        
        logger.info("Database collections initialized successfully")
        
    except Exception as e:
        logger.error("Failed to connect to MongoDB", error=str(e))
        raise


async def close_db() -> None:
    """Close database connection"""
    global client
    
    if client:
        client.close()
        logger.info("Database connection closed")


def get_database():
    """Get database instance"""
    return client[settings.DATABASE_NAME]
