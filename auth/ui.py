"""
auth/ui.py — Streamlit authentication gate for SAP Warehouse Agent.

Exposes a single public function:

    render_auth_gate() -> str

Call it at the top of app.py (after st.set_page_config).  It either
returns the authenticated user's email, or renders the login/signup UI
and calls st.stop() — preventing any downstream code from executing.

Internal helpers (_render_auth_ui, _render_login_form, _render_signup_form)
are private and not intended for external use.
"""

import streamlit as st

from auth.db import create_user, init_users_table, user_exists, verify_user


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_auth_gate() -> str:
    """
    Auth gate entry point.  Call once at the top of app.py.

    - If a user is already authenticated in session state → returns their email.
    - If not → renders the login / sign-up UI, then calls st.stop().

    Returns:
        str: The authenticated user's email (always lowercase-stripped).
    """
    init_users_table()

    if st.session_state.get("user"):
        return st.session_state["user"]

    _render_auth_ui()
    st.stop()  # Nothing below this executes until the user authenticates
    return ""  # Unreachable — satisfies type checkers


# ---------------------------------------------------------------------------
# Private UI helpers
# ---------------------------------------------------------------------------

def _render_auth_ui() -> None:
    """Renders the centred login/sign-up card."""
    st.markdown(
        """
        <style>
            /* Suppress default Streamlit chrome on the auth page */
            [data-testid="stHeader"]      { display: none; }
            [data-testid="stSidebarNav"]  { display: none; }
            /* Push content down a little for visual balance */
            .block-container { padding-top: 6rem !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _, col, _ = st.columns([1, 1.4, 1])

    with col:
        st.markdown(
            """
            <div style='text-align:center; margin-bottom:1.5rem'>
                <span style='font-size:3rem'>📦</span>
                <h2 style='margin:0.25rem 0 0.1rem'>SAP Warehouse Agent</h2>
                <p style='color:grey; margin:0'>Enterprise Warehouse Intelligence</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        login_tab, signup_tab = st.tabs(["🔑  Login", "✨  Sign Up"])

        with login_tab:
            _render_login_form()

        with signup_tab:
            _render_signup_form()


def _render_login_form() -> None:
    """Renders the login form and handles submission."""
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input(
            "Email", placeholder="you@company.com", key="login_email"
        )
        password = st.text_input(
            "Password", type="password", key="login_password"
        )
        submitted = st.form_submit_button(
            "Login", use_container_width=True, type="primary"
        )

    if submitted:
        if not email or not password:
            st.error("Please fill in both fields.")
        elif verify_user(email, password):
            st.session_state["user"] = email.lower().strip()
            st.rerun()
        else:
            st.error("Invalid email or password.")


def _render_signup_form() -> None:
    """Renders the account creation form and handles submission."""
    with st.form("signup_form", clear_on_submit=False):
        email = st.text_input(
            "Email", placeholder="you@company.com", key="signup_email"
        )
        password = st.text_input(
            "Password", type="password", key="signup_password"
        )
        confirm = st.text_input(
            "Confirm Password", type="password", key="signup_confirm"
        )
        submitted = st.form_submit_button(
            "Create Account", use_container_width=True, type="primary"
        )

    if submitted:
        if not email or not password or not confirm:
            st.error("Please fill in all fields.")
        elif password != confirm:
            st.error("Passwords do not match.")
        elif user_exists(email):
            st.error("An account with this email already exists. Please log in.")
        else:
            create_user(email, password)
            st.session_state["user"] = email.lower().strip()
            st.rerun()
