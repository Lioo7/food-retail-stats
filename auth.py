"""
Falafel Bribua — Authentication Gate
=====================================
Simple password gate using Streamlit secrets.

Setup (for Streamlit Community Cloud deployment):
  1. Create a file at .streamlit/secrets.toml
  2. Add:  password = "your-secret-password"
  3. The file is gitignored — never commit it.

When no secret is configured (local use), the gate is skipped entirely.
"""

import streamlit as st

from ui.styles import inject_css


def check_password() -> bool:
    """Return True if the user is authenticated (or auth is not configured).

    When ``st.secrets`` contains a ``password`` key the user must enter it
    before accessing the dashboard.  If no secret is set (typical for local
    runs), access is granted automatically.
    """
    try:
        expected = st.secrets["password"]
    except (KeyError, FileNotFoundError):
        # No password configured — allow access (local / unconfigured deploy)
        return True

    if st.session_state.get("authenticated"):
        return True

    # Inject CSS so the login card styles are available
    inject_css()

    # Centered login card
    st.markdown(
        '<div class="login-card">'
        '<div class="login-icon">🧆</div>'
        "<h2>פלאפל בריבוע</h2>"
        "<p>הזן סיסמה כדי להיכנס</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Center the form widgets using columns as gutters
    _left, center, _right = st.columns([1.2, 2, 1.2])
    with center:
        password = st.text_input("סיסמה", type="password", key="password_input",
                                 label_visibility="collapsed",
                                 placeholder="סיסמה")

        if st.button("כניסה", use_container_width=True, type="primary"):
            if password == expected:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ סיסמה שגויה. נסה שוב.")

    return False
