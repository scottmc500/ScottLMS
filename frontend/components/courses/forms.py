"""
Course form components
"""

import streamlit as st

from frontend.components.utils import make_api_request


def create_course_form():
    """Create course form"""
    st.subheader("➕ Create New Course")

    # Get users for instructor selection
    users_result = make_api_request("GET", "/api/users/")
    instructors = []

    if users_result["success"]:
        instructors = [u for u in users_result["data"] if u.get("role") == "instructor"]

    with st.form("create_course"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Course Title", placeholder="Introduction to Python")
            description = st.text_area(
                "Description", placeholder="Learn Python programming..."
            )

        with col2:
            if instructors:
                instructor_options = {
                    f"{i['first_name']} {i['last_name']}": i["id"] for i in instructors
                }
                selected_instructor = st.selectbox(
                    "Instructor", list(instructor_options.keys())
                )
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
                    "status": status,
                }

                result = make_api_request("POST", "/api/courses/", course_data)

                if result["success"]:
                    st.success("✅ Course created successfully! Check the 'View Courses' tab to see the new course.")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to create course: {result['error']}")


def edit_course_form(course):
    """Edit course form"""
    st.markdown("---")
    st.subheader("✏️ Edit Course")

    # Get users for instructor selection
    users_result = make_api_request("GET", "/api/users/")
    instructors = []

    if users_result["success"]:
        instructors = [u for u in users_result["data"] if u.get("role") == "instructor"]

    with st.form(f"edit_course_{course.get('id')}"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Course Title", value=course.get("title", ""))
            description = st.text_area("Description", value=course.get("description", ""))

        with col2:
            if instructors:
                instructor_options = {
                    f"{i['first_name']} {i['last_name']}": i["id"] for i in instructors
                }
                # Find current instructor name
                current_instructor_id = course.get("instructor_id")
                current_instructor_name = None
                for name, inst_id in instructor_options.items():
                    if inst_id == current_instructor_id:
                        current_instructor_name = name
                        break

                if current_instructor_name:
                    selected_instructor = st.selectbox(
                        "Instructor",
                        list(instructor_options.keys()),
                        index=list(instructor_options.keys()).index(current_instructor_name),
                    )
                else:
                    selected_instructor = st.selectbox("Instructor", list(instructor_options.keys()))

                instructor_id = instructor_options[selected_instructor]
            else:
                st.warning("No instructors found.")
                instructor_id = course.get("instructor_id")

            price = st.number_input("Price ($)", min_value=0.0, value=course.get("price", 0.0), step=0.01)
            status = st.selectbox(
                "Status",
                ["draft", "published"],
                index=["draft", "published"].index(course.get("status", "draft")),
            )

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Update Course", type="primary")
        with col2:
            if st.form_submit_button("Cancel"):
                del st.session_state.selected_course_for_edit
                st.rerun()

        if submitted:
            course_data = {
                "title": title,
                "description": description,
                "instructor_id": instructor_id,
                "price": price,
                "status": status,
            }

            result = make_api_request("PUT", f"/api/courses/{course.get('id')}", course_data)

            if result["success"]:
                st.success("✅ Course updated successfully!")
                del st.session_state.selected_course_for_edit
                st.rerun()
            else:
                st.error(f"❌ Failed to update course: {result['error']}")


def delete_course_confirmation(course):
    """Delete course confirmation form"""
    st.markdown("---")
    st.subheader("🗑️ Delete Course")
    st.warning(f"⚠️ Are you sure you want to delete course: {course.get('title', '')}?")
    st.info(f"**Description:** {course.get('description', '')}")
    st.info(f"**Price:** ${course.get('price', 0):.2f}")
    st.info(f"**Status:** {course.get('status', '').title()}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete Course", type="primary"):
            result = make_api_request("DELETE", f"/api/courses/{course.get('id')}")

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



