"""
Table display components for the frontend
"""
import streamlit as st
from typing import List, Dict, Any
from frontend.components.utils import make_api_request
from frontend.components.forms import edit_user_form, edit_course_form, delete_user_confirmation, delete_course_confirmation

def display_user_details(user):
    """Display detailed user information"""
    st.markdown("---")
    st.subheader(f"👤 User Details: {user.get('first_name', '')} {user.get('last_name', '')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Name:** {user.get('first_name', '')} {user.get('last_name', '')}")
        st.markdown(f"**Email:** {user.get('email', '')}")
        st.markdown(f"**Role:** {user.get('role', '').title()}")
        st.markdown(f"**User ID:** {user.get('id', '')}")
    
    with col2:
        if st.button("✏️ Edit User", key=f"edit_user_{user.get('id', '')}"):
            st.session_state.edit_user = user
            st.rerun()
        
        if st.button("🗑️ Delete User", key=f"delete_user_{user.get('id', '')}"):
            st.session_state.delete_user = user
            st.rerun()
    
    # Show edit form if editing
    if hasattr(st.session_state, 'edit_user') and st.session_state.edit_user.get('id') == user.get('id'):
        edit_user_form(user)
    
    # Show delete confirmation if deleting
    if hasattr(st.session_state, 'delete_user') and st.session_state.delete_user.get('id') == user.get('id'):
        delete_user_confirmation(user)

def display_course_details(course):
    """Display detailed course information"""
    st.markdown("---")
    st.subheader(f"📖 Course Details: {course.get('title', '')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Title:** {course.get('title', '')}")
        st.markdown(f"**Description:** {course.get('description', '')}")
        st.markdown(f"**Price:** ${course.get('price', 0):.2f}")
        st.markdown(f"**Status:** {course.get('status', '').title()}")
        st.markdown(f"**Course ID:** {course.get('id', '')}")
        st.markdown(f"**Instructor ID:** {course.get('instructor_id', '')}")
    
    with col2:
        if st.button("✏️ Edit Course", key=f"edit_course_{course.get('id', '')}"):
            st.session_state.edit_course = course
            st.rerun()
        
        if st.button("🗑️ Delete Course", key=f"delete_course_{course.get('id', '')}"):
            st.session_state.delete_course = course
            st.rerun()
    
    # Show edit form if editing
    if hasattr(st.session_state, 'edit_course') and st.session_state.edit_course.get('id') == course.get('id'):
        edit_course_form(course)
    
    # Show delete confirmation if deleting
    if hasattr(st.session_state, 'delete_course') and st.session_state.delete_course.get('id') == course.get('id'):
        delete_course_confirmation(course)

def display_users():
    """Display users section"""
    st.subheader("👥 Users")
    
    # Get users
    result = make_api_request("GET", "/users/")
    
    if result["success"]:
        users = result["data"]
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", len(users))
        with col2:
            instructors = len([u for u in users if u.get("role") == "instructor"])
            st.metric("Instructors", instructors)
        with col3:
            students = len([u for u in users if u.get("role") == "student"])
            st.metric("Students", students)
        
        # Search and filter
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 Search users", placeholder="Search by name or email...")
        with col2:
            role_filter = st.selectbox("Filter by role", ["All", "student", "instructor", "admin"])
        
        # Filter users
        filtered_users = users
        if search_term:
            filtered_users = [u for u in filtered_users if 
                            search_term.lower() in u.get("first_name", "").lower() or
                            search_term.lower() in u.get("last_name", "").lower() or
                            search_term.lower() in u.get("email", "").lower()]
        
        if role_filter != "All":
            filtered_users = [u for u in filtered_users if u.get("role") == role_filter]
        
        # Users table with clickable rows
        if filtered_users:
            # Create a selectbox for user selection
            user_options = {f"{u.get('first_name', '')} {u.get('last_name', '')} ({u.get('email', '')})": u for u in filtered_users}
            selected_user_display = st.selectbox("Select a user to view details:", list(user_options.keys()))
            
            if selected_user_display:
                selected_user = user_options[selected_user_display]
                display_user_details(selected_user)
            
            # Display filtered table
            st.dataframe(filtered_users, use_container_width=True)
        else:
            st.info("No users found matching your criteria")
    else:
        st.error(result["error"])

def display_courses():
    """Display courses section"""
    st.subheader("📚 Courses")
    
    # Get courses
    result = make_api_request("GET", "/courses/")
    
    if result["success"]:
        courses = result["data"]
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Courses", len(courses))
        with col2:
            published = len([c for c in courses if c.get("status") == "published"])
            st.metric("Published", published)
        with col3:
            total_price = sum([c.get("price", 0) for c in courses])
            st.metric("Total Value", f"${total_price:,.2f}")
        
        # Search and filter
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_term = st.text_input("🔍 Search courses", placeholder="Search by title or description...", key="course_search")
        with col2:
            status_filter = st.selectbox("Filter by status", ["All", "draft", "published"], key="course_status_filter")
        with col3:
            price_filter = st.selectbox("Filter by price", ["All", "Free", "Paid"], key="course_price_filter")
        
        # Filter courses
        filtered_courses = courses
        if search_term:
            filtered_courses = [c for c in filtered_courses if 
                              search_term.lower() in c.get("title", "").lower() or
                              search_term.lower() in c.get("description", "").lower()]
        
        if status_filter != "All":
            filtered_courses = [c for c in filtered_courses if c.get("status") == status_filter]
        
        if price_filter == "Free":
            filtered_courses = [c for c in filtered_courses if c.get("price", 0) == 0]
        elif price_filter == "Paid":
            filtered_courses = [c for c in filtered_courses if c.get("price", 0) > 0]
        
        # Courses table with clickable rows
        if filtered_courses:
            # Create a selectbox for course selection
            course_options = {f"{c.get('title', '')} - ${c.get('price', 0):.2f}": c for c in filtered_courses}
            selected_course_display = st.selectbox("Select a course to view details:", list(course_options.keys()))
            
            if selected_course_display:
                selected_course = course_options[selected_course_display]
                display_course_details(selected_course)
            
            # Display filtered table
            st.dataframe(filtered_courses, use_container_width=True)
        else:
            st.info("No courses found matching your criteria")
    else:
        st.error(result["error"])

def display_enrollments():
    """Display enrollments section"""
    st.subheader("🎯 Enrollments")
    
    # Get enrollments
    result = make_api_request("GET", "/enrollments/")
    
    if result["success"]:
        enrollments = result["data"]
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Enrollments", len(enrollments))
        with col2:
            active = len([e for e in enrollments if e.get("status") == "active"])
            st.metric("Active", active)
        with col3:
            completed = len([e for e in enrollments if e.get("status") == "completed"])
            st.metric("Completed", completed)
        
        # Enrollments table
        if enrollments:
            st.dataframe(enrollments, use_container_width=True)
        else:
            st.info("No enrollments found")
    else:
        st.error(result["error"])
