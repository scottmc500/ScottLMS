"""
Simple tests for the main FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import patch

# Add backend to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app


class TestMainApp:
    """Test main FastAPI application"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        # Mock the database initialization to avoid connection issues
        with patch('main.init_db'):
            return TestClient(app)

    @pytest.mark.backend
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    @pytest.mark.backend
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    @pytest.mark.backend
    def test_docs_endpoint(self, client):
        """Test API documentation endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200

    @pytest.mark.backend
    def test_openapi_endpoint(self, client):
        """Test OpenAPI schema endpoint"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()

