"""
Simple tests for frontend components
"""

import pytest
import sys
import os
from unittest.mock import patch, Mock

# Add frontend to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestComponents:
    """Test frontend components"""

    @pytest.mark.frontend
    def test_import_utils(self):
        """Test that utils module can be imported"""
        try:
            from components.utils import get_api_status, make_api_request
            assert callable(get_api_status)
            assert callable(make_api_request)
        except ImportError as e:
            pytest.fail(f"Failed to import utils: {e}")

    @pytest.mark.frontend
    def test_import_config(self):
        """Test that config module can be imported"""
        try:
            from config import API_BASE_URL, PAGE_CONFIG
            assert API_BASE_URL is not None
            assert PAGE_CONFIG is not None
        except ImportError as e:
            pytest.fail(f"Failed to import config: {e}")

    @pytest.mark.frontend
    @patch('components.utils.requests.get')
    def test_get_api_status_success(self, mock_get):
        """Test get_api_status with successful response"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_get.return_value = mock_response

        from components.utils import get_api_status
        result = get_api_status()

        assert result["success"] is True
        assert result["data"]["status"] == "healthy"
        mock_get.assert_called_once()

    @pytest.mark.frontend
    @patch('components.utils.requests.get')
    def test_get_api_status_failure(self, mock_get):
        """Test get_api_status with failed response"""
        # Mock failed response
        mock_get.side_effect = Exception("Connection failed")

        from components.utils import get_api_status
        result = get_api_status()

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.frontend
    def test_password_validation_import(self):
        """Test that password validation can be imported"""
        try:
            from components.shared.password_validation import validate_password
            assert callable(validate_password)
        except ImportError as e:
            pytest.fail(f"Failed to import password validation: {e}")

