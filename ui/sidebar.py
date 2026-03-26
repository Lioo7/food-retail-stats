"""Sidebar: branding, date picker, file uploader, platform info."""

import os
import datetime
import streamlit as st


def render_sidebar():
    """Render the sidebar and return (report_date, uploaded_files, download_placeholder)."""
    with st.sidebar:
        st.markdown("## 🧆 פלאפל בריבוע")
        st.caption("דוח מכירות יומי")
        st.divider()

        report_date = st.date_input(
            "📅 תאריך הדוח",
            value=datetime.date.today(),
            format="DD/MM/YYYY",
        )

        st.divider()

        uploaded_files = st.file_uploader(
            "📁 העלאת קבצים (7)",
            type=["csv", "xlsx", "xls", "pdf"],
            accept_multiple_files=True,
            help=(
                "העלה את כל 7 קבצי היום:\n"
                "• CSV מכר כולל מע\"מ\n"
                "• 3 קבצי Excel (ממוצע עסקה, מנות, שעות)\n"
                "• 3 קבצי PDF (מכירות פז + מנות פז)"
            ),
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} קבצים הועלו")

        sidebar_download_placeholder = st.empty()

        st.divider()
        _platform = "🪟 Windows" if os.name == "nt" else "🍎 macOS / Linux"
        st.caption(f"מערכת הפעלה: {_platform}")

    return report_date, uploaded_files, sidebar_download_placeholder
