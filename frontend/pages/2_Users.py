"""
User Management Page
"""

import streamlit as st

from frontend.components.users import create_user_form, display_users
from frontend.components.utils import get_api_status
from frontend.config import CUSTOM_CSS, PAGE_CONFIG

# Configure the page
st.set_page_config(**PAGE_CONFIG)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">👥 User Management</h1>', unsafe_allow_html=True)

# API Status in sidebar
st.sidebar.subheader("API Status")

health_result = get_api_status()
if health_result["success"]:
    st.sidebar.success("🟢 API Connected")
else:
    st.sidebar.error("🔴 API Disconnected")
    st.sidebar.error(health_result["error"])

# Main content - check if we should switch to View Users tab after creation
if st.session_state.get("switch_to_view_users", False):
    st.session_state.switch_to_view_users = False
    # Show success message and users list
    st.success("✅ User created successfully!")
    display_users()
else:
    tab1, tab2 = st.tabs(["📋 View Users", "➕ Create User"])

    with tab1:
        display_users()

    with tab2:
        create_user_form()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "ScottLMS User Management | Built with Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
