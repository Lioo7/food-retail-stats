"""Data table display and debug expander."""

import datetime
import pandas as pd
import streamlit as st


def render_data_table(merged: pd.DataFrame):
    """Render the formatted data table."""
    st.markdown("---")
    st.subheader("📋 טבלת נתונים")

    display_df = merged.copy()
    display_df['מכר כולל מע"מ'] = display_df['מכר כולל מע"מ'].apply(
        lambda x: f"₪{x:,.0f}" if pd.notna(x) else ""
    )
    display_df["ממוצע עסקאות"] = display_df["ממוצע עסקאות"].apply(
        lambda x: f"{x:.2f}" if pd.notna(x) else ""
    )
    display_df["מס' עסקאות"] = display_df["מס' עסקאות"].apply(
        lambda x: f"{int(x)}" if pd.notna(x) else ""
    )
    display_df["עסקה ראשונה"] = display_df["עסקה ראשונה"].apply(
        lambda x: x.strftime("%H:%M") if isinstance(x, datetime.time) else (str(x) if pd.notna(x) else "")
    )
    display_df["עסקה אחרונה"] = display_df["עסקה אחרונה"].apply(
        lambda x: x.strftime("%H:%M") if isinstance(x, datetime.time) else (str(x) if pd.notna(x) else "")
    )
    display_df["מנות בפיתה"] = display_df["מנות בפיתה"].apply(
        lambda x: f"{int(x)}" if pd.notna(x) else ""
    )
    display_df["ארוחות בפיתה"] = display_df["ארוחות בפיתה"].apply(
        lambda x: f"{int(x)}" if pd.notna(x) else ""
    )
    display_df["אחוז ארוחות מתוך מנות"] = display_df["אחוז ארוחות מתוך מנות"].apply(
        lambda x: f"{x:.1%}" if pd.notna(x) and x > 0 else "0%"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )


def render_debug(csv_data, avg_trans_data, portions_data, hourly_data,
                 paz_sales_list, paz_portions_list):
    """Render the raw-data debug expander."""
    with st.expander("🔧 נתונים גולמיים (Debug)", expanded=False):
        if csv_data is not None and not csv_data.empty:
            st.write("**CSV מכר:**")
            st.dataframe(csv_data, hide_index=True)
        if avg_trans_data is not None and not avg_trans_data.empty:
            st.write("**ממוצע עסקה:**")
            st.dataframe(avg_trans_data, hide_index=True)
        if portions_data is not None and not portions_data.empty:
            st.write("**מנות בפיתה:**")
            st.dataframe(portions_data, hide_index=True)
        if hourly_data is not None and not hourly_data.empty:
            st.write("**עסקאות לפי שעה:**")
            st.dataframe(hourly_data, hide_index=True)
        for i, ps in enumerate(paz_sales_list):
            st.write(f"**PDF מכירות פז #{i+1}:**")
            st.dataframe(ps, hide_index=True)
        for i, pp in enumerate(paz_portions_list):
            st.write(f"**PDF מנות פז #{i+1}:**")
            st.dataframe(pp, hide_index=True)
