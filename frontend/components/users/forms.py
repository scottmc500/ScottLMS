"""
User form components
"""

import streamlit as st

from components.utils import make_api_request
from components.shared.password_validation import (
    validate_password,
    display_inline_password_requirements,
)


def create_user_form():
    """Create user form"""
    st.subheader("➕ Create New User")

    # Check if we should reset the form (after successful creation)
    if st.session_state.get("form_reset_needed", False):
        st.session_state.form_reset_needed = False
        # Use a unique key to force form reset
        form_key = f"create_user_form_{st.session_state.get('form_counter', 0) + 1}"
        st.session_state.form_counter = st.session_state.get("form_counter", 0) + 1
    else:
        form_key = "create_user_form"

    with st.form(form_key):
        # Personal Information Section
        st.markdown("**👤 Personal Information**")
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", placeholder="John")
        with col2:
            last_name = st.text_input("Last Name", placeholder="Doe")

        email = st.text_input("Email", placeholder="john.doe@example.com")
        username = st.text_input("Username", placeholder="johndoe")

        # Account Settings Section
        st.markdown("**⚙️ Account Settings**")
        role = st.selectbox("Role", ["student", "instructor", "admin"])

        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input(
                "Password", type="password", placeholder="Enter strong password"
            )
        with col2:
            password_confirm = st.text_input(
                "Confirm Password", type="password", placeholder="Re-enter password"
            )

        submitted = st.form_submit_button("Create User", type="primary")

        if submitted:
            if not all(
                [first_name, last_name, email, username, password, password_confirm]
            ):
                st.error("Please fill in all required fields")
            elif password != password_confirm:
                st.error(
                    "❌ Passwords do not match. Please ensure both password fields are identical."
                )
            else:
                # Comprehensive password validation
                is_valid, errors = validate_password(
                    password, username, first_name, last_name, email
                )
                if not is_valid:
                    st.error("❌ Password does not meet requirements:")
                    for error in errors:
                        st.error(f"• {error}")
                    st.info(
                        "💡 **Password Requirements:**\n- 8-128 characters\n- Uppercase & lowercase letters\n- Numbers & special characters\n- No common passwords\n- No personal information"
                    )
                else:
                    user_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "username": username,
                        "role": role,
                        "password": password,
                    }

                    result = make_api_request("POST", "/api/users/", user_data)

                    if result["success"]:
                        # Set flags to reset form and switch to users view
                        st.session_state.form_reset_needed = True
                        st.session_state.switch_to_view_users = True
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to create user: {result['error']}")


def edit_user_form(user):
    """Edit user form"""
    st.markdown("---")
    st.subheader("✏️ Edit User")

    # Personal Information Section
    st.markdown("**👤 Personal Information**")
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input(
            "First Name",
            value=user.get("first_name", ""),
            key=f"edit_user_first_name_{user.get('id')}",
        )
    with col2:
        last_name = st.text_input(
            "Last Name",
            value=user.get("last_name", ""),
            key=f"edit_user_last_name_{user.get('id')}",
        )

    email = st.text_input(
        "Email", value=user.get("email", ""), key=f"edit_user_email_{user.get('id')}"
    )
    username = st.text_input(
        "Username",
        value=user.get("username", ""),
        key=f"edit_user_username_{user.get('id')}",
    )

    # Account Settings Section
    st.markdown("**⚙️ Account Settings**")
    role = st.selectbox(
        "Role",
        ["student", "instructor", "admin"],
        index=["student", "instructor", "admin"].index(user.get("role", "student")),
        key=f"edit_user_role_{user.get('id')}",
    )

    col1, col2 = st.columns(2)
    with col1:
        password = st.text_input(
            "New Password (leave blank to keep current)",
            type="password",
            placeholder="Enter strong password",
            key=f"edit_user_password_{user.get('id')}",
        )
    with col2:
        password_confirm = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter password",
            key=f"edit_user_password_confirm_{user.get('id')}",
        )

    # Action buttons outside form
    col1, col2 = st.columns(2)
    with col1:
        submitted = st.button(
            "Update User", type="primary", key=f"update_user_btn_{user.get('id')}"
        )
    with col2:
        if st.button("Cancel", key=f"cancel_user_btn_{user.get('id')}"):
            del st.session_state.selected_user_for_edit
            st.rerun()

    if submitted:
        # Validate password if provided
        if password:
            # Check if passwords match
            if password != password_confirm:
                st.error(
                    "❌ Passwords do not match. Please ensure both password fields are identical."
                )
                return

            is_valid, errors = validate_password(
                password, username, first_name, last_name, email
            )
            if not is_valid:
                st.error("❌ Password does not meet requirements:")
                for error in errors:
                    st.error(f"• {error}")
                st.info(
                    "💡 **Password Requirements:**\n- 8-128 characters\n- Uppercase & lowercase letters\n- Numbers & special characters\n- No common passwords\n- No personal information"
                )
                return

        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username": username,
            "role": role,
        }

        if password:
            user_data["password"] = password

        result = make_api_request("PUT", f"/api/users/{user.get('id')}", user_data)

        if result["success"]:
            st.success("✅ User updated successfully!")
            del st.session_state.selected_user_for_edit
            st.rerun()
        else:
            st.error(f"❌ Failed to update user: {result['error']}")


def delete_user_confirmation(user):
    """Delete user confirmation form"""
    st.markdown("---")
    st.subheader("🗑️ Delete User")
    st.warning(
        f"⚠️ Are you sure you want to delete user: {user.get('first_name', '')} {user.get('last_name', '')}?"
    )
    st.info(f"**Email:** {user.get('email', '')}")
    st.info(f"**Username:** {user.get('username', '')}")
    st.info(f"**Role:** {user.get('role', '').title()}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete User", type="primary"):
            result = make_api_request("DELETE", f"/api/users/{user.get('id')}")

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
