"""Parser for the CSV revenue file (מכר כולל מעמ.csv)."""

import io
import pandas as pd
import streamlit as st

from logic.merge import normalize_branch


@st.cache_data
def parse_csv_revenue(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """Parse the מכר כולל מעמ.csv file → DataFrame with [סניף, מכר כולל מע"מ].

    Encoding strategy (cross-platform):
      1. utf-8-sig  – Mac/Linux default (UTF-8 with optional BOM)
      2. cp1255     – Windows Hebrew code-page (very common on Israeli Windows)
      3. utf-8      – plain UTF-8 without BOM
      4. iso-8859-8 – legacy Hebrew ISO encoding
    The first encoding that produces no UnicodeDecodeError wins.
    """
    df = None
    tried = []
    for enc in ["utf-8-sig", "cp1255", "utf-8", "iso-8859-8"]:
        try:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding=enc)
            sample = " ".join(str(c) for c in df.columns)
            if any("\u05d0" <= ch <= "\u05ea" for ch in sample):
                break
            tried.append(enc)
            df = None
        except (UnicodeDecodeError, Exception):
            tried.append(enc)
            df = None

    if df is None:
        try:
            df = pd.read_csv(
                io.BytesIO(file_bytes), encoding="cp1255", encoding_errors="replace"
            )
        except Exception:
            raise ValueError(
                f"לא ניתן לקרוא את קובץ ה-CSV: {file_name}\n"
                f"Tried encodings: {tried}"
            )

    # Find revenue column — MUST be column D ("בחירת מדד").
    # Column E header misleadingly says "כולל מע"מ" but contains different data.
    # Column D holds the actual gross revenue including VAT.
    rev_col = None

    # Strategy 1: look for "בחירת מדד" by name
    for c in df.columns:
        if "בחירת מדד" in str(c):
            rev_col = c
            break

    # Strategy 2: fall back to positional column D (index 3)
    if rev_col is None and len(df.columns) >= 4:
        rev_col = df.columns[3]

    # Strategy 3: last resort — pick the first numeric column with "כולל מע"
    if rev_col is None:
        for c in df.columns:
            if "כולל מע" in str(c):
                rev_col = c
                break

    if rev_col is None:
        raise ValueError("לא נמצאה עמודת מכר כולל מע\"מ בקובץ CSV")

    # Find site column
    site_col = None
    for c in df.columns:
        if "site" in str(c).lower() or "סניף" in str(c) or "חנות" in str(c):
            site_col = c
            break
    if site_col is None:
        site_col = df.columns[0]

    result = pd.DataFrame()
    result["סניף"] = df[site_col].apply(lambda x: normalize_branch(str(x)))
    result['מכר כולל מע"מ'] = pd.to_numeric(df[rev_col], errors="coerce")

    # Also extract transaction count if available
    trans_col = None
    for c in df.columns:
        if "הזמנות" in str(c):
            trans_col = c
            break
    if trans_col:
        result["הזמנות_csv"] = pd.to_numeric(df[trans_col], errors="coerce")

    result = result.dropna(subset=['מכר כולל מע"מ'])
    result = result[result["סניף"] != "Total"]
    return result
