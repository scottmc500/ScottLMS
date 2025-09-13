"""
Course Management Page
"""

import streamlit as st

from frontend.components.forms import create_course_form
from frontend.components.tables import display_courses
from frontend.components.utils import get_api_status
from frontend.config import CUSTOM_CSS, PAGE_CONFIG

# Configure the page
st.set_page_config(**PAGE_CONFIG)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📚 Course Management</h1>', unsafe_allow_html=True)

# API Status in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("API Status")

health_result = get_api_status()
if health_result["success"]:
    st.sidebar.success("🟢 API Connected")
else:
    st.sidebar.error("🔴 API Disconnected")
    st.sidebar.error(health_result["error"])

# Main content
tab1, tab2 = st.tabs(["📋 View Courses", "➕ Create Course"])

with tab1:
    display_courses()

with tab2:
    create_course_form()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "ScottLMS Course Management | Built with Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
