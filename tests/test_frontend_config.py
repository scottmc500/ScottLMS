"""
Tests for frontend configuration and utilities
"""

import pytest
import os
import sys

# Add frontend to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'frontend'))

from frontend.config import API_BASE_URL


class TestFrontendConfig:
    """Test frontend configuration"""
    
    @pytest.mark.frontend
    def test_api_base_url_default(self):
        """Test default API base URL"""
        # Test that API_BASE_URL is set (could be default or environment override)
        assert API_BASE_URL in ["http://localhost", "http://localhost:8000"]
    
    @pytest.mark.frontend
    def test_api_base_url_environment_override(self):
        """Test API base URL with environment variable"""
        # Set environment variable
        os.environ["API_BASE_URL"] = "http://test-api:8000"
        
        # Re-import to get the new value
        import importlib
        import frontend.config
        importlib.reload(frontend.config)
        
        assert frontend.config.API_BASE_URL == "http://test-api:8000"
        
        # Clean up
        del os.environ["API_BASE_URL"]
        importlib.reload(frontend.config)
