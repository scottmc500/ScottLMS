"""
User table and display components
"""

import streamlit as st

from components.utils import make_api_request
from .forms import edit_user_form, delete_user_confirmation


def display_user_details(user):
    """Display detailed user information"""
    st.markdown("---")
    st.subheader(
        f"👤 User Details: {user.get('first_name', '')} {user.get('last_name', '')}"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"**Name:** {user.get('first_name', '')} {user.get('last_name', '')}"
        )
        st.markdown(f"**Email:** {user.get('email', '')}")
        st.markdown(f"**Role:** {user.get('role', '').title()}")
        st.markdown(f"**User ID:** {user.get('id', '')}")

    with col2:
        if st.button("✏️ Edit User", key=f"edit_user_{user.get('id', '')}"):
            st.session_state.selected_user_for_edit = user
            st.rerun()

        if st.button("🗑️ Delete User", key=f"delete_user_{user.get('id', '')}"):
            st.session_state.delete_user = user
            st.rerun()

    # Show edit form if editing
    if hasattr(
        st.session_state, "selected_user_for_edit"
    ) and st.session_state.selected_user_for_edit.get("id") == user.get("id"):
        edit_user_form(st.session_state.selected_user_for_edit)

    # Show delete confirmation if deleting
    if hasattr(st.session_state, "delete_user") and st.session_state.delete_user.get(
        "id"
    ) == user.get("id"):
        delete_user_confirmation(user)


def display_users():
    """Display users section"""
    st.subheader("👥 Users")

    # Get users
    result = make_api_request("GET", "/api/users/")

    if result["success"]:
        users = result["data"]

        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", len(users))
        with col2:
            students = len([u for u in users if u.get("role") == "student"])
            st.metric("Students", students)
        with col3:
            instructors = len([u for u in users if u.get("role") == "instructor"])
            st.metric("Instructors", instructors)

        # Search and filter
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term = st.text_input(
                "🔍 Search users", placeholder="Search by name, email, or username"
            )
        with col2:
            role_filter = st.selectbox(
                "Filter by role", ["All", "student", "instructor", "admin"]
            )
        with col3:
            sort_by = st.selectbox("Sort by", ["Name", "Email", "Role", "Created"])

        # Filter users
        filtered_users = users
        if search_term:
            search_lower = search_term.lower()
            filtered_users = [
                u
                for u in filtered_users
                if (
                    search_lower in u.get("first_name", "").lower()
                    or search_lower in u.get("last_name", "").lower()
                    or search_lower in u.get("email", "").lower()
                    or search_lower in u.get("username", "").lower()
                )
            ]

        if role_filter != "All":
            filtered_users = [u for u in filtered_users if u.get("role") == role_filter]

        # Sort users
        if sort_by == "Name":
            filtered_users.sort(
                key=lambda x: f"{x.get('first_name', '')} {x.get('last_name', '')}"
            )
        elif sort_by == "Email":
            filtered_users.sort(key=lambda x: x.get("email", ""))
        elif sort_by == "Role":
            filtered_users.sort(key=lambda x: x.get("role", ""))
        elif sort_by == "Created":
            filtered_users.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        # Display filtered results
        if filtered_users:
            st.info(f"Showing {len(filtered_users)} of {len(users)} users")

            # Pagination
            items_per_page = 5
            total_pages = (len(filtered_users) + items_per_page - 1) // items_per_page

            if total_pages > 1:
                # Initialize page state
                if "users_current_page" not in st.session_state:
                    st.session_state.users_current_page = 1

                # Navigation controls with better column spacing
                nav_col1, nav_col2, nav_col3 = st.columns([2, 3, 2])

                with nav_col1:
                    if st.button(
                        "⬅️ Prev",
                        disabled=st.session_state.users_current_page <= 1,
                        key="users_prev",
                    ):
                        st.session_state.users_current_page -= 1
                        st.rerun()

                with nav_col2:
                    page = st.selectbox(
                        "Page",
                        range(1, total_pages + 1),
                        index=st.session_state.users_current_page - 1,
                        key="users_page_selector",
                        on_change=lambda: setattr(
                            st.session_state,
                            "users_current_page",
                            st.session_state.users_page_selector,
                        ),
                    )

                with nav_col3:
                    if st.button(
                        "Next ➡️",
                        disabled=st.session_state.users_current_page >= total_pages,
                        key="users_next",
                    ):
                        st.session_state.users_current_page += 1
                        st.rerun()

                # Calculate start and end indices
                start_idx = (st.session_state.users_current_page - 1) * items_per_page
                end_idx = min(start_idx + items_per_page, len(filtered_users))

                st.info(
                    f"Showing users {start_idx + 1}-{end_idx} of {len(filtered_users)}"
                )

                # Display users for current page
                for user in filtered_users[start_idx:end_idx]:
                    display_user_details(user)
            else:
                # Display all users if only one page
                for user in filtered_users:
                    display_user_details(user)
        else:
            st.info("No users found matching your criteria")
    else:
        st.error(result["error"])
