"""
Rate limiting configuration for ScottLMS
Centralized rate limiting setup with enum-based limits
"""

from enum import Enum
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address


class RateLimit(Enum):
    """Rate limit configurations for different HTTP methods"""
    
    # HTTP Method-based limits
    GET = "200/minute"      # Read operations (users, courses, enrollments)
    POST = "50/minute"      # Create operations (new users, courses, enrollments)  
    PUT = "50/minute"       # Update operations (modify existing data)
    DELETE = "20/minute"    # Delete operations (remove data)
    
    # Special endpoint limits (for future use)
    # AUTH = "10/minute"      # Authentication endpoints
    # ADMIN = "100/minute"    # Admin-only endpoints


# Create shared limiter instance
limiter = Limiter(key_func=get_remote_address)

def setup_rate_limiting(app: FastAPI) -> None:
    """
    Configure rate limiting for the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    # Add rate limiting error handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
