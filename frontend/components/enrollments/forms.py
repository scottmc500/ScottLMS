"""
Enrollment form components
"""

import streamlit as st

from frontend.components.utils import make_api_request


def create_enrollment_form():
    """Create enrollment form"""
    st.subheader("➕ Create New Enrollment")

    # Get users and courses
    users_result = make_api_request("GET", "/api/users/")
    courses_result = make_api_request("GET", "/api/courses/")

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
                student_options = {
                    f"{s['first_name']} {s['last_name']} ({s['email']})": s["id"]
                    for s in students
                }
                selected_student = st.selectbox("Student", list(student_options.keys()))
                student_id = student_options[selected_student]
            else:
                st.warning("No students found. Create a student first.")
                student_id = None

        with col2:
            if courses:
                course_options = {
                    f"{c['title']} - ${c['price']:.2f}": c["id"] for c in courses
                }
                selected_course = st.selectbox("Course", list(course_options.keys()))
                course_id = course_options[selected_course]
            else:
                st.warning(
                    "No published courses found. Create a published course first."
                )
                course_id = None

        status = st.selectbox("Enrollment Status", ["active", "completed", "dropped"])

        submitted = st.form_submit_button("Create Enrollment", type="primary")

        if submitted:
            if not all([student_id, course_id]):
                st.error("Please select both a student and a course")
            else:
                enrollment_data = {
                    "user_id": student_id,
                    "course_id": course_id,
                    "status": status,
                }

                result = make_api_request("POST", "/api/enrollments/", enrollment_data)

                if result["success"]:
                    st.success("✅ Enrollment created successfully! Check the 'View Enrollments' tab to see the new enrollment.")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to create enrollment: {result['error']}")


def edit_enrollment_form(enrollment):
    """Edit enrollment form"""
    st.markdown("---")
    st.subheader("✏️ Edit Enrollment")

    with st.form("edit_enrollment"):
        col1, col2 = st.columns(2)

        with col1:
            status = st.selectbox(
                "Status",
                ["active", "completed", "paused", "cancelled"],
                index=["active", "completed", "paused", "cancelled"].index(
                    enrollment.get("status", "active")
                ),
            )

        with col2:
            progress = st.number_input(
                "Progress (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(enrollment.get("progress", 0)),
                step=1.0,
            )

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Update Enrollment", type="primary")
        with col2:
            if st.form_submit_button("Cancel"):
                del st.session_state.selected_enrollment_for_edit
                st.rerun()

        if submitted:
            enrollment_data = {
                "status": status,
                "progress": progress,
            }

            result = make_api_request("PUT", f"/api/enrollments/{enrollment.get('id')}", enrollment_data)

            if result["success"]:
                st.success("✅ Enrollment updated successfully!")
                del st.session_state.selected_enrollment_for_edit
                st.rerun()
            else:
                st.error(f"❌ Failed to update enrollment: {result['error']}")


def delete_enrollment_form(enrollment):
    """Delete enrollment confirmation form"""
    st.markdown("---")
    st.subheader("🗑️ Delete Enrollment")
    st.warning(f"⚠️ Are you sure you want to delete this enrollment?")
    st.info(f"**User ID:** {enrollment.get('user_id', '')}")
    st.info(f"**Course ID:** {enrollment.get('course_id', '')}")
    st.info(f"**Status:** {enrollment.get('status', '').title()}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete Enrollment", type="primary"):
            result = make_api_request("DELETE", f"/api/enrollments/{enrollment.get('id')}")

            if result["success"]:
                st.success("✅ Enrollment deleted successfully!")
                del st.session_state.delete_enrollment
                st.rerun()
            else:
                st.error(f"❌ Failed to delete enrollment: {result['error']}")

    with col2:
        if st.button("Cancel"):
            del st.session_state.delete_enrollment
            st.rerun()



