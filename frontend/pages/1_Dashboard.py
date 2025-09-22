"""
Dashboard page - Main overview of the LMS
"""

import streamlit as st

from frontend.components.users import display_users
from frontend.components.courses import display_courses
from frontend.components.enrollments import display_enrollments
from frontend.components.utils import get_api_status
from frontend.config import CUSTOM_CSS


def show_dashboard():
    """Display the main dashboard"""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Header
    st.markdown(
        '<h1 class="main-header">📊 Data Dashboard</h1>', unsafe_allow_html=True
    )

    st.markdown("### 🔍 Detailed Data Management & Analytics")
    st.markdown(
        "View and analyze all your LMS data in detail. Use this page for comprehensive data management tasks."
    )

    # API Status check
    st.sidebar.subheader("API Status")

    health_result = get_api_status()
    if health_result["success"]:
        st.sidebar.success("🟢 API Connected")
    else:
        st.sidebar.error("🔴 API Disconnected")
        st.sidebar.error(health_result["error"])

    # Main content
    st.markdown("### 📋 Complete Data Tables")

    # Display all data
    display_users()
    st.markdown("---")
    display_courses()
    st.markdown("---")
    display_enrollments()

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "📊 Data Dashboard | Return to <a href='/' style='color: #1f77b4;'>Home</a> for overview"
        "</div>",
        unsafe_allow_html=True,
    )


# Execute the dashboard
show_dashboard()
