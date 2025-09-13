"""
Form components for the frontend
"""
import streamlit as st
from typing import Dict, Any
from frontend.components.utils import make_api_request

def create_user_form():
    """Create user form"""
    st.subheader("➕ Create New User")
    
    with st.form("create_user"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name", placeholder="John")
            last_name = st.text_input("Last Name", placeholder="Doe")
            email = st.text_input("Email", placeholder="john.doe@example.com")
        
        with col2:
            role = st.selectbox("Role", ["student", "instructor", "admin"])
            password = st.text_input("Password", type="password", placeholder="Enter password")
        
        submitted = st.form_submit_button("Create User", type="primary")
        
        if submitted:
            if not all([first_name, last_name, email, password]):
                st.error("Please fill in all required fields")
            else:
                user_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "role": role,
                    "password": password
                }
                
                result = make_api_request("POST", "/users/", user_data)
                
                if result["success"]:
                    st.success("✅ User created successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to create user: {result['error']}")

def create_course_form():
    """Create course form"""
    st.subheader("➕ Create New Course")
    
    # Get users for instructor selection
    users_result = make_api_request("GET", "/users/")
    instructors = []
    
    if users_result["success"]:
        instructors = [u for u in users_result["data"] if u.get("role") == "instructor"]
    
    with st.form("create_course"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Course Title", placeholder="Introduction to Python")
            description = st.text_area("Description", placeholder="Learn Python programming...")
        
        with col2:
            if instructors:
                instructor_options = {f"{i['first_name']} {i['last_name']}": i['id'] for i in instructors}
                selected_instructor = st.selectbox("Instructor", list(instructor_options.keys()))
                instructor_id = instructor_options[selected_instructor]
            else:
                st.warning("No instructors found. Create an instructor first.")
                instructor_id = None
            
            price = st.number_input("Price ($)", min_value=0.0, value=99.99, step=0.01)
            status = st.selectbox("Status", ["draft", "published"])
        
        submitted = st.form_submit_button("Create Course", type="primary")
        
        if submitted:
            if not all([title, description, instructor_id]):
                st.error("Please fill in all required fields")
            else:
                course_data = {
                    "title": title,
                    "description": description,
                    "instructor_id": instructor_id,
                    "price": price,
                    "status": status
                }
                
                result = make_api_request("POST", "/courses/", course_data)
                
                if result["success"]:
                    st.success("✅ Course created successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to create course: {result['error']}")

def create_enrollment_form():
    """Create enrollment form"""
    st.subheader("➕ Create New Enrollment")
    
    # Get users and courses
    users_result = make_api_request("GET", "/users/")
    courses_result = make_api_request("GET", "/courses/")
    
    students = []
    courses = []
    
    if users_result["success"]:
        students = [u for u in users_result["data"] if u.get("role") == "student"]
    
    if courses_result["success"]:
        courses = [c for c in courses_result["data"] if c.get("status") == "published"]
    
    with st.form("create_enrollment"):
        col1, col2 = st.columns(2)
        
        with col1:
            if students:
                student_options = {f"{s['first_name']} {s['last_name']} ({s['email']})": s['id'] for s in students}
                selected_student = st.selectbox("Student", list(student_options.keys()))
                student_id = student_options[selected_student]
            else:
                st.warning("No students found. Create a student first.")
                student_id = None
        
        with col2:
            if courses:
                course_options = {f"{c['title']} - ${c['price']:.2f}": c['id'] for c in courses}
                selected_course = st.selectbox("Course", list(course_options.keys()))
                course_id = course_options[selected_course]
            else:
                st.warning("No published courses found. Create a published course first.")
                course_id = None
        
        status = st.selectbox("Enrollment Status", ["active", "completed", "dropped"])
        
        submitted = st.form_submit_button("Create Enrollment", type="primary")
        
        if submitted:
            if not all([student_id, course_id]):
                st.error("Please select both a student and a course")
            else:
                enrollment_data = {
                    "student_id": student_id,
                    "course_id": course_id,
                    "status": status
                }
                
                result = make_api_request("POST", "/enrollments/", enrollment_data)
                
                if result["success"]:
                    st.success("✅ Enrollment created successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to create enrollment: {result['error']}")

def edit_user_form(user):
    """Edit user form"""
    st.markdown("---")
    st.subheader("✏️ Edit User")
    
    with st.form("edit_user"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name", value=user.get("first_name", ""))
            last_name = st.text_input("Last Name", value=user.get("last_name", ""))
            email = st.text_input("Email", value=user.get("email", ""))
        
        with col2:
            role = st.selectbox("Role", ["student", "instructor", "admin"], 
                              index=["student", "instructor", "admin"].index(user.get("role", "student")))
            password = st.text_input("New Password (leave blank to keep current)", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Update User", type="primary")
        with col2:
            if st.form_submit_button("Cancel"):
                del st.session_state.edit_user
                st.rerun()
        
        if submitted:
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "role": role
            }
            
            if password:
                user_data["password"] = password
            
            result = make_api_request("PUT", f"/users/{user.get('id')}", user_data)
            
            if result["success"]:
                st.success("✅ User updated successfully!")
                del st.session_state.edit_user
                st.rerun()
            else:
                st.error(f"❌ Failed to update user: {result['error']}")

def edit_course_form(course):
    """Edit course form"""
    st.markdown("---")
    st.subheader("✏️ Edit Course")
    
    # Get users for instructor selection
    users_result = make_api_request("GET", "/users/")
    instructors = []
    
    if users_result["success"]:
        instructors = [u for u in users_result["data"] if u.get("role") == "instructor"]
    
    with st.form("edit_course"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Course Title", value=course.get("title", ""))
            description = st.text_area("Description", value=course.get("description", ""))
        
        with col2:
            if instructors:
                instructor_options = {f"{i['first_name']} {i['last_name']}": i['id'] for i in instructors}
                current_instructor = None
                for i in instructors:
                    if i['id'] == course.get('instructor_id'):
                        current_instructor = f"{i['first_name']} {i['last_name']}"
                        break
                
                selected_instructor = st.selectbox("Instructor", list(instructor_options.keys()),
                                                 index=list(instructor_options.keys()).index(current_instructor) if current_instructor else 0)
                instructor_id = instructor_options[selected_instructor]
            else:
                st.warning("No instructors found.")
                instructor_id = course.get("instructor_id")
            
            price = st.number_input("Price ($)", min_value=0.0, value=course.get("price", 0.0), step=0.01)
            status = st.selectbox("Status", ["draft", "published"],
                                index=["draft", "published"].index(course.get("status", "draft")))
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Update Course", type="primary")
        with col2:
            if st.form_submit_button("Cancel"):
                del st.session_state.edit_course
                st.rerun()
        
        if submitted:
            course_data = {
                "title": title,
                "description": description,
                "instructor_id": instructor_id,
                "price": price,
                "status": status
            }
            
            result = make_api_request("PUT", f"/courses/{course.get('id')}", course_data)
            
            if result["success"]:
                st.success("✅ Course updated successfully!")
                del st.session_state.edit_course
                st.rerun()
            else:
                st.error(f"❌ Failed to update course: {result['error']}")

def delete_user_confirmation(user):
    """Delete user confirmation"""
    st.markdown("---")
    st.warning(f"⚠️ Are you sure you want to delete user: {user.get('first_name', '')} {user.get('last_name', '')}?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete User", type="primary"):
            result = make_api_request("DELETE", f"/users/{user.get('id')}")
            
            if result["success"]:
                st.success("✅ User deleted successfully!")
                del st.session_state.delete_user
                st.rerun()
            else:
                st.error(f"❌ Failed to delete user: {result['error']}")
    
    with col2:
        if st.button("Cancel"):
            del st.session_state.delete_user
            st.rerun()

def delete_course_confirmation(course):
    """Delete course confirmation"""
    st.markdown("---")
    st.warning(f"⚠️ Are you sure you want to delete course: {course.get('title', '')}?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete Course", type="primary"):
            result = make_api_request("DELETE", f"/courses/{course.get('id')}")
            
            if result["success"]:
                st.success("✅ Course deleted successfully!")
                del st.session_state.delete_course
                st.rerun()
            else:
                st.error(f"❌ Failed to delete course: {result['error']}")
    
    with col2:
        if st.button("Cancel"):
            del st.session_state.delete_course
            st.rerun()
