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

    st.markdown(
        "<h2 style='text-align:center;'>🧆 פלאפל בריבוע</h2>"
        "<p style='text-align:center;'>הזן סיסמה כדי להיכנס</p>",
        unsafe_allow_html=True,
    )

    password = st.text_input("סיסמה", type="password", key="password_input")

    if st.button("כניסה", use_container_width=True):
        if password == expected:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ סיסמה שגויה. נסה שוב.")

    return False
