"""
Enrollment table and display components
"""

import streamlit as st

from components.utils import make_api_request
from .forms import edit_enrollment_form, delete_enrollment_form


def display_enrollment_details(enrollment):
    """Display enrollment details with edit/delete options"""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"**Status:** {enrollment.get('status', '').title()}")
        st.markdown(f"**Progress:** {enrollment.get('progress', 0)}%")
        st.markdown(f"**User ID:** {enrollment.get('user_id', '')}")
        st.markdown(f"**Course ID:** {enrollment.get('course_id', '')}")
        st.markdown(f"**Enrollment ID:** {enrollment.get('id', '')}")

    with col2:
        # Create unique keys using user_id and course_id as fallback if ID is missing
        enrollment_id = enrollment.get('id', '') or enrollment.get('_id', '') or f"{enrollment.get('user_id', '')}_{enrollment.get('course_id', '')}"
        edit_key = f"edit_enrollment_{enrollment_id}_{hash(str(enrollment))}"
        delete_key = f"delete_enrollment_{enrollment_id}_{hash(str(enrollment))}"
        
        if st.button("✏️ Edit Enrollment", key=edit_key):
            st.session_state.selected_enrollment_for_edit = enrollment
            st.rerun()

        if st.button("🗑️ Delete Enrollment", key=delete_key):
            st.session_state.delete_enrollment = enrollment
            st.rerun()

    # Show edit form if editing
    if hasattr(
        st.session_state, "selected_enrollment_for_edit"
    ) and st.session_state.selected_enrollment_for_edit.get("id") == enrollment.get(
        "id"
    ):
        edit_enrollment_form(st.session_state.selected_enrollment_for_edit)

    # Show delete confirmation if deleting
    if hasattr(
        st.session_state, "delete_enrollment"
    ) and st.session_state.delete_enrollment.get("id") == enrollment.get("id"):
        delete_enrollment_form(enrollment)


def display_enrollments():
    """Display enrollments section"""
    st.subheader("🎯 Enrollments")

    # Get enrollments
    result = make_api_request("GET", "/api/enrollments/")

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

        # Search and filter
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox(
                "Filter by status",
                ["All", "active", "completed", "paused", "cancelled"],
            )
        with col2:
            progress_filter = st.selectbox(
                "Filter by progress", ["All", "0-25%", "26-50%", "51-75%", "76-100%"]
            )
        with col3:
            sort_by = st.selectbox("Sort by", ["Status", "Progress", "Enrolled Date"])

        # Filter enrollments
        filtered_enrollments = enrollments
        if status_filter != "All":
            filtered_enrollments = [
                e for e in filtered_enrollments if e.get("status") == status_filter
            ]

        if progress_filter != "All":
            if progress_filter == "0-25%":
                filtered_enrollments = [
                    e for e in filtered_enrollments if 0 <= e.get("progress", 0) <= 25
                ]
            elif progress_filter == "26-50%":
                filtered_enrollments = [
                    e for e in filtered_enrollments if 26 <= e.get("progress", 0) <= 50
                ]
            elif progress_filter == "51-75%":
                filtered_enrollments = [
                    e for e in filtered_enrollments if 51 <= e.get("progress", 0) <= 75
                ]
            elif progress_filter == "76-100%":
                filtered_enrollments = [
                    e for e in filtered_enrollments if 76 <= e.get("progress", 0) <= 100
                ]

        # Sort enrollments
        if sort_by == "Status":
            filtered_enrollments.sort(key=lambda x: x.get("status", ""))
        elif sort_by == "Progress":
            filtered_enrollments.sort(key=lambda x: x.get("progress", 0), reverse=True)
        elif sort_by == "Enrolled Date":
            filtered_enrollments.sort(
                key=lambda x: x.get("enrolled_at", ""), reverse=True
            )

        # Display filtered results
        if filtered_enrollments:
            st.info(
                f"Showing {len(filtered_enrollments)} of {len(enrollments)} enrollments"
            )

            # Pagination
            items_per_page = 5
            total_pages = (
                len(filtered_enrollments) + items_per_page - 1
            ) // items_per_page

            if total_pages > 1:
                # Initialize page state
                if "enrollments_current_page" not in st.session_state:
                    st.session_state.enrollments_current_page = 1

                # Navigation controls with better column spacing
                nav_col1, nav_col2, nav_col3 = st.columns([2, 3, 2])

                with nav_col1:
                    if st.button(
                        "⬅️ Prev",
                        disabled=st.session_state.enrollments_current_page <= 1,
                        key="enrollments_prev",
                    ):
                        st.session_state.enrollments_current_page -= 1
                        st.rerun()

                with nav_col2:
                    page = st.selectbox(
                        "Page",
                        range(1, total_pages + 1),
                        index=st.session_state.enrollments_current_page - 1,
                        key="enrollments_page_selector",
                        on_change=lambda: setattr(
                            st.session_state,
                            "enrollments_current_page",
                            st.session_state.enrollments_page_selector,
                        ),
                    )

                with nav_col3:
                    if st.button(
                        "Next ➡️",
                        disabled=st.session_state.enrollments_current_page
                        >= total_pages,
                        key="enrollments_next",
                    ):
                        st.session_state.enrollments_current_page += 1
                        st.rerun()

                # Calculate start and end indices
                start_idx = (
                    st.session_state.enrollments_current_page - 1
                ) * items_per_page
                end_idx = min(start_idx + items_per_page, len(filtered_enrollments))

                st.info(
                    f"Showing enrollments {start_idx + 1}-{end_idx} of {len(filtered_enrollments)}"
                )

                # Display enrollments for current page
                for enrollment in filtered_enrollments[start_idx:end_idx]:
                    display_enrollment_details(enrollment)
                    st.markdown("---")
            else:
                # Display all enrollments if only one page
                for enrollment in filtered_enrollments:
                    display_enrollment_details(enrollment)
                    st.markdown("---")
        else:
            st.info("No enrollments found matching your criteria")
    else:
        st.error(result["error"])
