"""KPI card rendering — hero revenue + 4 secondary metrics."""

import pandas as pd
import streamlit as st


def render_kpi_cards(merged: pd.DataFrame):
    """Render the hero revenue card and 4 secondary KPI cards."""
    total_revenue = merged['מכר כולל מע"מ'].sum()
    total_portions = merged["מנות בפיתה"].sum()
    total_transactions = merged["מס' עסקאות"].sum()
    top_branch = (
        merged.loc[merged['מכר כולל מע"מ'].idxmax(), "סניף"]
        if not merged['מכר כולל מע"מ'].isna().all()
        else "N/A"
    )
    top_revenue = merged['מכר כולל מע"מ'].max()
    num_active = len(merged[merged['מכר כולל מע"מ'] > 0])

    # Row 1: Revenue — the hero metric
    with st.container(border=True):
        st.markdown(
            f'<div class="kpi-hero"><h3>מכר כולל יומי</h3><h1>₪{total_revenue:,.0f}</h1></div>',
            unsafe_allow_html=True,
        )

        # Row 2: Secondary KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f'<div class="kpi-card kpi-green"><h3>סה"כ עסקאות</h3><h1>{total_transactions:,.0f}</h1></div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f'<div class="kpi-card kpi-orange"><h3>סה"כ מנות</h3><h1>{total_portions:,.0f}</h1></div>',
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f'<div class="kpi-card kpi-blue"><h3>סניף מוביל</h3>'
                f'<h1>{top_branch}</h1>'
                f'<p>₪{top_revenue:,.0f}</p></div>',
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f'<div class="kpi-card kpi-purple"><h3>סניפים פעילים</h3><h1>{num_active}</h1></div>',
                unsafe_allow_html=True,
            )
