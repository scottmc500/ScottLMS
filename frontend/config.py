"""
Frontend configuration settings
"""

import os
from pathlib import Path

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page configuration
PAGE_CONFIG = {"page_title": "ScottLMS Dashboard", "page_icon": "🎓", "layout": "wide"}


def load_css() -> str:
    """Load custom CSS from external file"""
    css_file = Path(__file__).parent / "styles.css"
    try:
        with open(css_file, "r", encoding="utf-8") as f:
            css_content = f.read()
        return f"<style>{css_content}</style>"
    except FileNotFoundError:
        # Fallback CSS if file not found
        return """
        <style>
        .main-header {
            font-size: 3rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        </style>
        """


# Custom CSS loaded from external file
CUSTOM_CSS = load_css()
