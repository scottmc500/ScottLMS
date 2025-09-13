"""
Utility functions for the frontend
"""
import requests
from typing import Dict, Any
from frontend.config import API_BASE_URL

def make_api_request(method: str, endpoint: str, data: Dict = None) -> Dict:
    """Make API request and handle errors"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        # Add headers to handle Docker networking
        headers = {
            'Host': 'api:8000',
            'User-Agent': 'ScottLMS-Frontend/1.0'
        }
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"API Error {response.status_code}: {response.text}"}
    
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to API. Make sure the API is running on http://localhost"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "API request timed out"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def get_api_status() -> Dict:
    """Check API connection status"""
    return make_api_request("GET", "/health")
