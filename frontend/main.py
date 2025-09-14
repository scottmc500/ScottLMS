"""
Main Streamlit application entry point
This is the new main file for the refactored ScottLMS frontend
"""

import streamlit as st

from frontend.config import PAGE_CONFIG
from frontend.pages.dashboard import show_dashboard

# Configure the page
st.set_page_config(**PAGE_CONFIG)

# Show the dashboard
show_dashboard()
