"""
Enrollment Management Page
"""

import streamlit as st

from frontend.components.enrollments import create_enrollment_form, display_enrollments
from frontend.components.utils import get_api_status
from frontend.config import CUSTOM_CSS, PAGE_CONFIG

# Configure the page
st.set_page_config(**PAGE_CONFIG)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Header
st.markdown(
    '<h1 class="main-header">🎯 Enrollment Management</h1>', unsafe_allow_html=True
)

# API Status in sidebar
st.sidebar.subheader("API Status")

health_result = get_api_status()
if health_result["success"]:
    st.sidebar.success("🟢 API Connected")
else:
    st.sidebar.error("🔴 API Disconnected")
    st.sidebar.error(health_result["error"])

# Main content
tab1, tab2 = st.tabs(["📋 View Enrollments", "➕ Create Enrollment"])

with tab1:
    display_enrollments()

with tab2:
    create_enrollment_form()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "ScottLMS Enrollment Management | Built with Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
