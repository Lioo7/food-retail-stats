"""Parsers for the three Excel input files."""

import io
import datetime
import pandas as pd
import streamlit as st

from logic.merge import normalize_branch


@st.cache_data
def parse_xlsx_avg_trans(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """Parse ממוצע עסקה+מס' עסקאות.xlsx → [סניף, ממוצע עסקאות, מס' עסקאות]."""
    df = pd.read_excel(io.BytesIO(file_bytes), header=None)

    # Find the header row
    header_row = 0
    for i in range(min(5, len(df))):
        row_str = " ".join(str(v) for v in df.iloc[i] if pd.notna(v))
        if "סניף" in row_str or "ממוצע" in row_str:
            header_row = i
            break

    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    # Find relevant columns
    site_col = avg_col = trans_col = None
    for c in df.columns:
        cs = str(c)
        if "סניף" in cs or "site" in cs.lower():
            site_col = c
        elif "ממוצע" in cs:
            avg_col = c
        elif "הזמנות" in cs:
            trans_col = c

    if site_col is None:
        site_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
    if avg_col is None:
        avg_col = df.columns[2] if len(df.columns) > 2 else None
    if trans_col is None:
        trans_col = df.columns[3] if len(df.columns) > 3 else None

    result = pd.DataFrame()
    result["סניף"] = df[site_col].apply(
        lambda x: normalize_branch(str(x)) if pd.notna(x) else None
    )
    if avg_col is not None:
        result["ממוצע עסקאות"] = pd.to_numeric(df[avg_col], errors="coerce")
    if trans_col is not None:
        result["מס' עסקאות"] = pd.to_numeric(df[trans_col], errors="coerce")

    result = result.dropna(subset=["סניף"])
    result = result[~result["סניף"].isin(["Total", "nan", "None"])]
    return result


@st.cache_data
def parse_xlsx_portions(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """Parse סהכ מנות מול ארוחה בפיתה.xlsx → [סניף, מנות בפיתה, ארוחות בפיתה]."""
    df = pd.read_excel(io.BytesIO(file_bytes), header=None)

    branch_data = {}
    current_branch = None

    for _, row in df.iterrows():
        branch_raw = str(row.iloc[0]) if pd.notna(row.iloc[0]) else None
        category = str(row.iloc[1]) if pd.notna(row.iloc[1]) else None
        qty = row.iloc[4] if len(row) > 4 and pd.notna(row.iloc[4]) else 0

        if branch_raw and branch_raw not in ("סניף", "nan", "Total", "None"):
            if "מסננים" in str(branch_raw):
                continue
            current_branch = normalize_branch(branch_raw)
            if current_branch not in branch_data:
                branch_data[current_branch] = {"total": 0, "meals": 0}

        if current_branch and category:
            qty_val = pd.to_numeric(qty, errors="coerce") or 0
            if category == "Total":
                branch_data[current_branch]["total"] = qty_val
            elif "ארוחה" in category:
                branch_data[current_branch]["meals"] = qty_val

    rows = []
    for branch, data in branch_data.items():
        total_portions = data["total"]
        meals = data["meals"]
        rows.append({
            "סניף": branch,
            "מנות בפיתה": int(total_portions) if total_portions else 0,
            "ארוחות בפיתה": int(meals) if meals else 0,
        })

    return pd.DataFrame(rows)


@st.cache_data
def parse_xlsx_hourly(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """Parse עסקאות לפי שעה.xlsx → [סניף, עסקה ראשונה, עסקה אחרונה]."""
    df = pd.read_excel(io.BytesIO(file_bytes), header=None)

    branch_times = {}
    current_branch = None

    for _, row in df.iterrows():
        branch_raw = str(row.iloc[0]) if pd.notna(row.iloc[0]) else None
        time_val = row.iloc[3] if len(row) > 3 and pd.notna(row.iloc[3]) else None

        if branch_raw and branch_raw not in ("nan", "סה\"כ", "None"):
            if "פלאפל" in branch_raw:
                current_branch = normalize_branch(branch_raw)
                if current_branch not in branch_times:
                    branch_times[current_branch] = []

        if current_branch and time_val is not None:
            time_str = str(time_val).strip()
            try:
                if isinstance(time_val, datetime.time):
                    branch_times[current_branch].append(time_val)
                elif ":" in time_str:
                    parts = time_str.split(":")
                    h, m = int(parts[0]), int(parts[1])
                    branch_times[current_branch].append(datetime.time(h, m))
            except (ValueError, IndexError):
                pass

    rows = []
    for branch, times in branch_times.items():
        if times:
            first = min(times)
            last = max(times)
            rows.append({
                "סניף": branch,
                "עסקה ראשונה": first,
                "עסקה אחרונה": last,
            })

    return pd.DataFrame(rows)
