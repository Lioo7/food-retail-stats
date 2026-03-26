"""Analytics section — Paz vs Chain split, ranking table, summary table."""

import datetime
import pandas as pd
import streamlit as st

from config import PAZ_BRANCHES


def render_analytics(merged: pd.DataFrame):
    """Render the analytics section (group split cards, ranking table, summary)."""
    total_revenue = merged['מכר כולל מע"מ'].sum()

    st.markdown('<div class="section-hdr">📈 ניתוח יומי</div>', unsafe_allow_html=True)

    # ── Paz vs Non-Paz split (metric cards) ──
    _paz_mask = merged["סניף"].isin(PAZ_BRANCHES)
    paz_rev = merged.loc[_paz_mask, 'מכר כולל מע"מ'].sum()
    non_paz_rev = merged.loc[~_paz_mask, 'מכר כולל מע"מ'].sum()
    paz_pct = paz_rev / total_revenue * 100 if total_revenue > 0 else 0
    non_paz_pct = non_paz_rev / total_revenue * 100 if total_revenue > 0 else 0
    paz_count = _paz_mask.sum()
    non_paz_count = (~_paz_mask).sum()

    gcol1, gcol2 = st.columns(2)
    with gcol1:
        st.markdown(
            f'<div class="grp-card grp-chain">'
            f'<h4>סניפי רשת ({non_paz_count})</h4>'
            f'<h2>₪{non_paz_rev:,.0f}</h2>'
            f'<p>{non_paz_pct:.1f}% מהמכר</p></div>',
            unsafe_allow_html=True,
        )
    with gcol2:
        st.markdown(
            f'<div class="grp-card grp-paz">'
            f'<h4>סניפי פז ({paz_count})</h4>'
            f'<h2>₪{paz_rev:,.0f}</h2>'
            f'<p>{paz_pct:.1f}% מהמכר</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Branch ranking table ──
    st.markdown("**דירוג סניפים לפי מכר**")

    ranking_df = merged.copy()
    ranking_df = ranking_df.sort_values('מכר כולל מע"מ', ascending=False).reset_index(drop=True)

    ranking_df["דירוג"] = range(1, len(ranking_df) + 1)
    ranking_df["% מהמכר"] = ranking_df['מכר כולל מע"מ'] / total_revenue if total_revenue > 0 else 0

    def _calc_hours(row):
        f = row.get("עסקה ראשונה")
        l = row.get("עסקה אחרונה")
        if isinstance(f, datetime.time) and isinstance(l, datetime.time):
            f_min = f.hour * 60 + f.minute
            l_min = l.hour * 60 + l.minute
            diff = l_min - f_min
            return round(diff / 60, 1) if diff > 0 else None
        return None

    ranking_df["שעות פעילות"] = ranking_df.apply(_calc_hours, axis=1)
    ranking_df["מכר לשעה"] = ranking_df.apply(
        lambda r: round(r['מכר כולל מע"מ'] / r["שעות פעילות"])
        if r["שעות פעילות"] and r["שעות פעילות"] > 0 else None,
        axis=1,
    )

    rank_display = ranking_df[["דירוג", "סניף", 'מכר כולל מע"מ', "% מהמכר",
                                "מס' עסקאות", "שעות פעילות", "מכר לשעה",
                                "מנות בפיתה", "ארוחות בפיתה"]].copy()

    n_branches = len(rank_display)

    def _highlight_rank(row):
        rank = row["דירוג"]
        if rank <= 3:
            return ["background-color: #FFF2CC"] * len(row)
        elif rank > n_branches - 3:
            return ["background-color: #FCE4EC"] * len(row)
        return [""] * len(row)

    styled_ranking = rank_display.style.apply(_highlight_rank, axis=1).format({
        'מכר כולל מע"מ': "₪{:,.0f}",
        "% מהמכר": "{:.1%}",
        "מס' עסקאות": lambda x: f"{int(x)}" if pd.notna(x) else "",
        "שעות פעילות": lambda x: f"{x:.1f}" if pd.notna(x) else "",
        "מכר לשעה": lambda x: f"₪{x:,.0f}" if pd.notna(x) else "",
        "מנות בפיתה": lambda x: f"{int(x)}" if pd.notna(x) else "",
        "ארוחות בפיתה": lambda x: f"{int(x)}" if pd.notna(x) else "",
    })

    st.dataframe(
        styled_ranking,
        use_container_width=True,
        hide_index=True,
        height=min(40 * n_branches + 60, 600),
    )

    # ── Paz vs Non-Paz summary table ──
    st.markdown("**סיכום: רשת מול פז**")

    paz_trans = merged.loc[_paz_mask, "מס' עסקאות"].sum()
    non_paz_trans = merged.loc[~_paz_mask, "מס' עסקאות"].sum()

    summary_rows = [
        {
            "קבוצה": "סניפי רשת",
            "סניפים": int(non_paz_count),
            'מכר כולל מע"מ': non_paz_rev,
            "% מהמכר": non_paz_pct / 100,
            "מס' עסקאות": int(non_paz_trans),
            "ממוצע מכר לסניף": round(non_paz_rev / non_paz_count) if non_paz_count > 0 else 0,
        },
        {
            "קבוצה": "סניפי פז",
            "סניפים": int(paz_count),
            'מכר כולל מע"מ': paz_rev,
            "% מהמכר": paz_pct / 100,
            "מס' עסקאות": int(paz_trans),
            "ממוצע מכר לסניף": round(paz_rev / paz_count) if paz_count > 0 else 0,
        },
        {
            "קבוצה": 'סה"כ',
            "סניפים": int(non_paz_count + paz_count),
            'מכר כולל מע"מ': total_revenue,
            "% מהמכר": 1.0,
            "מס' עסקאות": int(non_paz_trans + paz_trans),
            "ממוצע מכר לסניף": round(total_revenue / (non_paz_count + paz_count)) if (non_paz_count + paz_count) > 0 else 0,
        },
    ]
    summary_df = pd.DataFrame(summary_rows)

    st.dataframe(
        summary_df.style.format({
            'מכר כולל מע"מ': "₪{:,.0f}",
            "% מהמכר": "{:.1%}",
            "מס' עסקאות": "{:,.0f}",
            "ממוצע מכר לסניף": "₪{:,.0f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Return ranking_df for use by charts
    return ranking_df
