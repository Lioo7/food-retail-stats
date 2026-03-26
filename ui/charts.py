"""Chart section — revenue, efficiency, portions, meal %."""

import pandas as pd
import streamlit as st


def render_charts(merged: pd.DataFrame, ranking_df: pd.DataFrame):
    """Render the 4 chart sub-tabs."""
    st.markdown('<div class="section-hdr">📈 גרפים ומגמות</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 מכר לפי סניף",
        "⏱️ מכר לשעת פעילות",
        "🥙 מנות וארוחות",
        "📈 אחוז ארוחות",
    ])

    with tab1:
        chart_df = merged[["סניף", 'מכר כולל מע"מ']].copy()
        # Sort ascending so highest values render at the top of horizontal bars
        chart_df = chart_df.sort_values('מכר כולל מע"מ', ascending=True)
        st.bar_chart(
            chart_df.set_index("סניף")['מכר כולל מע"מ'],
            horizontal=True,
            use_container_width=True,
        )

    with tab2:
        rph_chart = ranking_df[["סניף", "מכר לשעה"]].copy()
        rph_chart = rph_chart.dropna(subset=["מכר לשעה"])
        rph_chart = rph_chart.sort_values("מכר לשעה", ascending=True)
        if not rph_chart.empty:
            st.bar_chart(
                rph_chart.set_index("סניף")["מכר לשעה"],
                horizontal=True,
                use_container_width=True,
            )
        else:
            st.info("אין נתוני שעות פעילות לחישוב מכר לשעה.")

    with tab3:
        portions_chart = merged[["סניף", "מנות בפיתה", "ארוחות בפיתה"]].copy()
        portions_chart = portions_chart.dropna(subset=["מנות בפיתה"])
        portions_chart = portions_chart.sort_values("מנות בפיתה", ascending=True)
        st.bar_chart(
            portions_chart.set_index("סניף")[["מנות בפיתה", "ארוחות בפיתה"]],
            horizontal=True,
            use_container_width=True,
        )

    with tab4:
        meal_chart = ranking_df[["סניף", "מנות בפיתה", "ארוחות בפיתה"]].copy()
        meal_chart = meal_chart[(meal_chart["מנות בפיתה"].notna()) & (meal_chart["מנות בפיתה"] > 0)]
        meal_chart["אחוז ארוחות"] = meal_chart["ארוחות בפיתה"] / meal_chart["מנות בפיתה"]
        meal_chart = meal_chart.sort_values("אחוז ארוחות", ascending=True)
        if not meal_chart.empty:
            st.bar_chart(
                meal_chart.set_index("סניף")["אחוז ארוחות"],
                horizontal=True,
                use_container_width=True,
            )
        else:
            st.info("אין נתוני מנות לחישוב אחוז ארוחות.")
