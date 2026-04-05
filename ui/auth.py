"""Password gate for the SOZO Generator app."""
import streamlit as st


def check_password() -> None:
    """Show a password gate and stop if not authenticated.

    If no secrets are configured (local dev) the gate is skipped entirely.
    On success the 'authenticated' key is set in session_state and the app
    continues normally.
    """
    if st.session_state.get("authenticated"):
        return

    try:
        correct = st.secrets["auth"]["password"]
    except Exception:
        # No secrets configured — skip gate in local dev
        return

    st.markdown("## SOZO Protocol Generator")
    st.markdown("Enter the access password to continue.")
    pwd = st.text_input("Password", type="password", key="pwd_input")
    if st.button("Login"):
        if pwd == correct:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()
