"""
Course table and display components
"""

import streamlit as st

from components.utils import make_api_request
from .forms import edit_course_form, delete_course_confirmation


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
            st.session_state.selected_course_for_edit = course
            st.rerun()

        if st.button("🗑️ Delete Course", key=f"delete_course_{course.get('id', '')}"):
            st.session_state.delete_course = course
            st.rerun()

    # Show edit form if editing
    if hasattr(
        st.session_state, "selected_course_for_edit"
    ) and st.session_state.selected_course_for_edit.get("id") == course.get("id"):
        edit_course_form(st.session_state.selected_course_for_edit)

    # Show delete confirmation if deleting
    if hasattr(
        st.session_state, "delete_course"
    ) and st.session_state.delete_course.get("id") == course.get("id"):
        delete_course_confirmation(course)


def display_courses():
    """Display courses section"""
    st.subheader("📚 Courses")

    # Get courses
    result = make_api_request("GET", "/api/courses/")

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
            drafts = len([c for c in courses if c.get("status") == "draft"])
            st.metric("Drafts", drafts)

        # Search and filter
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term = st.text_input(
                "🔍 Search courses", placeholder="Search by title or description..."
            )
        with col2:
            status_filter = st.selectbox(
                "Filter by status", ["All", "published", "draft"]
            )
        with col3:
            sort_by = st.selectbox("Sort by", ["Title", "Price", "Status", "Created"])

        # Filter courses
        filtered_courses = courses
        if search_term:
            filtered_courses = [
                c
                for c in filtered_courses
                if search_term.lower() in c.get("title", "").lower()
                or search_term.lower() in c.get("description", "").lower()
            ]

        if status_filter != "All":
            filtered_courses = [
                c for c in filtered_courses if c.get("status") == status_filter
            ]

        # Sort courses
        if sort_by == "Title":
            filtered_courses.sort(key=lambda x: x.get("title", ""))
        elif sort_by == "Price":
            filtered_courses.sort(key=lambda x: x.get("price", 0), reverse=True)
        elif sort_by == "Status":
            filtered_courses.sort(key=lambda x: x.get("status", ""))
        elif sort_by == "Created":
            filtered_courses.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        # Display filtered results
        if filtered_courses:
            st.info(f"Showing {len(filtered_courses)} of {len(courses)} courses")

            # Pagination
            items_per_page = 5
            total_pages = (len(filtered_courses) + items_per_page - 1) // items_per_page

            if total_pages > 1:
                # Initialize page state
                if "courses_current_page" not in st.session_state:
                    st.session_state.courses_current_page = 1

                # Navigation controls with better column spacing
                nav_col1, nav_col2, nav_col3 = st.columns([2, 3, 2])

                with nav_col1:
                    if st.button(
                        "⬅️ Prev",
                        disabled=st.session_state.courses_current_page <= 1,
                        key="courses_prev",
                    ):
                        st.session_state.courses_current_page -= 1
                        st.rerun()

                with nav_col2:
                    page = st.selectbox(
                        "Page",
                        range(1, total_pages + 1),
                        index=st.session_state.courses_current_page - 1,
                        key="courses_page_selector",
                        on_change=lambda: setattr(
                            st.session_state,
                            "courses_current_page",
                            st.session_state.courses_page_selector,
                        ),
                    )

                with nav_col3:
                    if st.button(
                        "Next ➡️",
                        disabled=st.session_state.courses_current_page >= total_pages,
                        key="courses_next",
                    ):
                        st.session_state.courses_current_page += 1
                        st.rerun()

                # Calculate start and end indices
                start_idx = (st.session_state.courses_current_page - 1) * items_per_page
                end_idx = min(start_idx + items_per_page, len(filtered_courses))

                st.info(
                    f"Showing courses {start_idx + 1}-{end_idx} of {len(filtered_courses)}"
                )

                # Display courses for current page
                for course in filtered_courses[start_idx:end_idx]:
                    display_course_details(course)
            else:
                # Display all courses if only one page
                for course in filtered_courses:
                    display_course_details(course)
        else:
            st.info("No courses found matching your criteria")
    else:
        st.error(result["error"])
