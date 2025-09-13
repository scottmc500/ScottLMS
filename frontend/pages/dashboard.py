"""
Dashboard page - Main overview of the LMS
"""
import streamlit as st
from frontend.components.tables import display_users, display_courses, display_enrollments
from frontend.components.utils import get_api_status
from frontend.config import CUSTOM_CSS

def show_dashboard():
    """Display the main dashboard"""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🎓 ScottLMS Dashboard</h1>', unsafe_allow_html=True)
    
    # API Status check
    st.sidebar.markdown("---")
    st.sidebar.subheader("API Status")
    
    health_result = get_api_status()
    if health_result["success"]:
        st.sidebar.success("🟢 API Connected")
    else:
        st.sidebar.error("🔴 API Disconnected")
        st.sidebar.error(health_result["error"])
    
    # Main content
    st.markdown("### 📊 System Overview")
    
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
        "ScottLMS Dashboard | Built with Streamlit | API: http://localhost"
        "</div>",
        unsafe_allow_html=True
    )
