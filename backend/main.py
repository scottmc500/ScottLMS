"""
ScottLMS - Simplified Learning Management System
Main FastAPI application entry point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from logs import setup_logging
from routers import users, courses, enrollments
from limiter import limiter, setup_rate_limiting, RateLimit


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_db()
    yield
    # Shutdown - cleanup if needed


# Create FastAPI application
app = FastAPI(
    title="ScottLMS",
    description="A simplified Learning Management System",
    version="1.0.0",
    lifespan=lifespan,
)

# Setup rate limiting
setup_rate_limiting(app)

# Setup logging
setup_logging()

# Add CORS middleware
import os

# Get allowed origins from environment or use defaults
ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS", 
    "http://localhost:80,http://localhost:8501,http://127.0.0.1:80,http://127.0.0.1:8501"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Specific origins only
    allow_credentials=True,  # Safe with specific origins
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Specific methods
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With"
    ],  # Specific headers only
    expose_headers=["X-Total-Count"],  # Only expose necessary headers
    max_age=3600,  # Cache preflight requests for 1 hour
)


@app.get("/")
@limiter.limit(RateLimit.GET.value)
async def root(request: Request):
    """Root endpoint"""
    return {"message": "Welcome to ScottLMS", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include API routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(enrollments.router, prefix="/api/enrollments", tags=["enrollments"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
