"""
Home page - Welcome and overview for ScottLMS
"""

import streamlit as st

from frontend.components.utils import get_api_status, make_api_request
from frontend.config import PAGE_CONFIG, CUSTOM_CSS

# Configure the page
st.set_page_config(**PAGE_CONFIG)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Header
st.markdown(
    '<h1 class="main-header">🎓 Welcome to ScottLMS</h1>', unsafe_allow_html=True
)

# API Status in sidebar
st.sidebar.subheader("API Status")

health_result = get_api_status()
if health_result["success"]:
    st.sidebar.success("🟢 API Connected")
    api_connected = True
else:
    st.sidebar.error("🔴 API Disconnected")
    st.sidebar.error(health_result["error"])
    api_connected = False

# Main content
st.markdown("### 👋 Getting Started")
st.markdown(
    """
Welcome to your Learning Management System! ScottLMS helps you manage users, courses, and enrollments all in one place.

Use the navigation menu on the left to:
- 👥 **Users**: Manage students and instructors
- 📚 **Courses**: Create and manage courses  
- 📝 **Enrollments**: Track student enrollments
- 📊 **Dashboard**: View detailed data and analytics
"""
)

# Quick Stats Section
st.markdown("### 📊 Quick Stats")

if api_connected:
    col1, col2, col3 = st.columns(3)

    # Get stats from API
    users_result = make_api_request("GET", "/api/users/")
    courses_result = make_api_request("GET", "/api/courses/")
    enrollments_result = make_api_request("GET", "/api/enrollments/")

    with col1:
        if users_result["success"]:
            user_count = len(users_result["data"])
            st.metric("👥 Total Users", user_count)
        else:
            st.metric("👥 Total Users", "Error")

    with col2:
        if courses_result["success"]:
            course_count = len(courses_result["data"])
            st.metric("📚 Total Courses", course_count)
        else:
            st.metric("📚 Total Courses", "Error")

    with col3:
        if enrollments_result["success"]:
            enrollment_count = len(enrollments_result["data"])
            st.metric("📝 Total Enrollments", enrollment_count)
        else:
            st.metric("📝 Total Enrollments", "Error")
else:
    st.error("📡 Cannot load stats - API is disconnected")

# Quick Actions Section
st.markdown("### 🚀 Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("👥 Manage Users", use_container_width=True):
        try:
            st.switch_page("pages/2_Users.py")
        except AttributeError:
            st.info("👥 Navigate to **Users** page using the sidebar menu")

with col2:
    if st.button("📚 Manage Courses", use_container_width=True):
        try:
            st.switch_page("pages/3_Courses.py")
        except AttributeError:
            st.info("📚 Navigate to **Courses** page using the sidebar menu")

with col3:
    if st.button("📝 Manage Enrollments", use_container_width=True):
        try:
            st.switch_page("pages/4_Enrollments.py")
        except AttributeError:
            st.info("📝 Navigate to **Enrollments** page using the sidebar menu")

with col4:
    if st.button("📊 View Dashboard", use_container_width=True):
        try:
            st.switch_page("pages/1_Dashboard.py")
        except AttributeError:
            st.info("📊 Navigate to **Dashboard** page using the sidebar menu")

# Recent Activity Section (placeholder for now)
st.markdown("### 📋 System Status")

if api_connected:
    st.success("✅ All systems operational")
    st.info(
        "💡 **Tip**: Use the Dashboard page for detailed data management and analytics"
    )
else:
    st.error("❌ API connection issues detected")
    st.warning(
        "🔧 Please check that the backend API is running on http://localhost:8000"
    )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "ScottLMS - Learning Management System | Built with ❤️ using Streamlit & FastAPI"
    "</div>",
    unsafe_allow_html=True,
)
