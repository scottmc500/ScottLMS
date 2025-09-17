"""
Tests for the main FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app, headers={"Host": "localhost"})


@pytest.mark.backend
def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to ScottLMS"


@pytest.mark.backend
def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ScottLMS"


@pytest.mark.backend
def test_api_docs_endpoint():
    """Test that API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


@pytest.mark.backend
def test_openapi_endpoint():
    """Test that OpenAPI schema is accessible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data


@pytest.mark.skip(reason="Requires database initialization - integration test")
def test_api_endpoints():
    """Test that API endpoints are accessible"""
    # Test users endpoint - should fail when no DB connection
    response = client.get("/users/")
    print(f"Users endpoint status: {response.status_code}")
    assert response.status_code in [500, 503]  # Database not initialized in tests
    
    # Test courses endpoint
    response = client.get("/courses/")
    print(f"Courses endpoint status: {response.status_code}")
    assert response.status_code in [500, 503]  # Database not initialized in tests
    
    # Test enrollments endpoint
    response = client.get("/enrollments/")
    print(f"Enrollments endpoint status: {response.status_code}")
    assert response.status_code in [500, 503]  # Database not initialized in tests
