"""
Database configuration and connection management
"""

import structlog
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from core.config import settings
from models.course import Course
from models.enrollment import Enrollment
from models.user import User

logger = structlog.get_logger()

# Global database client
client: AsyncIOMotorClient = None


async def init_db() -> None:
    """Initialize database connection and collections"""
    global client

    try:
        # Create MongoDB client with SSL disabled for DocumentDB
        # Parse and reconstruct the connection string properly
        from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
        import re
        
        # Parse the URL
        parsed = urlparse(settings.MONGODB_URL)
        
        # Remove ssl=true from query parameters
        query_params = parse_qs(parsed.query)
        if 'ssl' in query_params:
            del query_params['ssl']
        
        # Reconstruct the query string
        new_query = urlencode(query_params, doseq=True)
        
        # Reconstruct the URL
        connection_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        logger.info(f"Original MongoDB URL: {settings.MONGODB_URL}")
        logger.info(f"Parsed URL components: scheme={parsed.scheme}, netloc={parsed.netloc}, path={parsed.path}, query={parsed.query}")
        logger.info(f"Query parameters: {query_params}")
        logger.info(f"New query string: {new_query}")
        logger.info(f"Final connection URL: {connection_url}")
        client = AsyncIOMotorClient(connection_url, tls=False, tlsAllowInvalidCertificates=True)

        # Test connection
        await client.admin.command("ping")
        logger.info("Connected to MongoDB successfully")

        # Initialize Beanie with document models
        await init_beanie(
            database=client[settings.DATABASE_NAME],
            document_models=[User, Course, Enrollment],
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
