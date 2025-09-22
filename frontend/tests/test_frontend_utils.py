"""
Tests for frontend utilities
"""

from frontend.components.utils import make_api_request
import pytest
import os
import sys
from unittest.mock import patch, Mock

# Add frontend to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "frontend"))


class TestFrontendUtils:
    """Test frontend utility functions"""

    @pytest.mark.frontend
    def test_make_api_request_get_success(self):
        """Test successful GET request"""
        with patch("requests.get") as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.json.return_value = {"success": True, "data": "test"}
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            result = make_api_request("GET", "/test")

            assert result["success"] is True
            assert result["data"]["data"] == "test"
            mock_get.assert_called_once()

    @pytest.mark.frontend
    def test_make_api_request_post_success(self):
        """Test successful POST request"""
        with patch("requests.post") as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.json.return_value = {"success": True, "id": "123"}
            mock_response.status_code = 201
            mock_post.return_value = mock_response

            result = make_api_request("POST", "/test", {"name": "test"})

            assert result["success"] is True
            assert result["data"]["id"] == "123"
            mock_post.assert_called_once()

    @pytest.mark.frontend
    def test_make_api_request_connection_error(self):
        """Test connection error handling"""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Connection failed")

            result = make_api_request("GET", "/test")

            assert result["success"] is False
            assert "Unexpected error" in result["error"]

    @pytest.mark.frontend
    def test_make_api_request_invalid_method(self):
        """Test invalid HTTP method"""
        result = make_api_request("INVALID", "/test")

        assert result["success"] is False
        assert "Unexpected error" in result["error"]
