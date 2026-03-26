"""Parsers for Paz branch PDF files (sales and portions)."""

import io
import re
import datetime
import pandas as pd
import pdfplumber
import streamlit as st


# Known Paz store names in PDF (Hebrew, may appear reversed in text extraction)
# IMPORTANT: Longer/more-specific patterns must come BEFORE shorter ones
# so that e.g. "ךז םחתמ" is matched before a bare "ךז" would be.
PAZ_STORE_PATTERNS = {
    # רופין / זך — all these variants map to רופין:
    #   "מתחם זך - ליאת חג'ג'" → extracted as "'ג'גח תאיל - ךז םחתמ"
    #   "פלאפל זך"              → extracted as "ךז לפאלפ"
    "ךז םחתמ": "רופין",
    "ךז לפאלפ": "רופין",
    "חג'ג": "רופין",
    "ליאת": "רופין",
    "פלאפל זך": "רופין",
    "ךז": "רופין",
    # טופז
    "זפוט": "טופז",
    "טופז": "טופז",
    "ינוב רחש": "טופז",
    "שחר בוני": "טופז",
    # שקמה
    "המקש": "שקמה",
    "השקמה": "שקמה",
    # מנחם
    "םחנמ": "מנחם",
    "מנחם": "מנחם",
    # אשכול
    "לוכשא": "אשכול",
    "אשכול": "אשכול",
    # נחלת
    "תלחנ": "נחלת",
    "נחלת": "נחלת",
    # פז שוהם
    "םהוש לפאלפ": "פז שוהם",
    "פלאפל שוהם": "פז שוהם",
}


def _parse_time(s: str):
    """Try to parse a time string like '08:59:00' or '08:59'."""
    s = s.strip()
    parts = s.replace(":", " ").split()
    try:
        h, m = int(parts[0]), int(parts[1])
        return datetime.time(h, m)
    except (ValueError, IndexError):
        return None


def _parse_number(s: str) -> float:
    """Parse a number string, removing commas."""
    s = s.strip().replace(",", "").replace(" ", "")
    try:
        return float(s)
    except ValueError:
        return None


def _identify_paz_store(line: str) -> str:
    """Try to identify which Paz store a line refers to."""
    for pattern, master_name in PAZ_STORE_PATTERNS.items():
        if pattern in line:
            return master_name
    return None


@st.cache_data
def parse_pdf_sales(file_bytes: bytes, file_name: str, target_date: str) -> pd.DataFrame:
    """
    Parse a Paz מכירות חנות PDF.
    Extracts: revenue incl VAT, avg, num transactions, first/last time
    for the target_date only.

    target_date: 'DD.MM.YYYY' format
    """
    results = []

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            all_text = ""
            for page in pdf.pages:
                text = page.extract_text() or ""
                all_text += text + "\n"
    except Exception as e:
        st.warning(f"שגיאה בקריאת PDF מכירות: {file_name} - {e}")
        return pd.DataFrame()

    lines = all_text.split("\n")
    current_store = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        store = _identify_paz_store(line)
        if store:
            current_store = store

        if target_date not in line:
            continue

        if current_store is None:
            store = _identify_paz_store(line)
            if store:
                current_store = store
            else:
                continue

        # Find all time patterns
        time_pattern = r'(\d{1,2}:\d{2}(?::\d{2})?)'
        times = re.findall(time_pattern, line)

        # Remove times and date from line for number extraction
        clean_line = line
        for t in times:
            clean_line = clean_line.replace(t, " ")
        clean_line = clean_line.replace(target_date, " ")

        number_parts = re.findall(r'[\d,]+\.?\d*', clean_line)
        numbers = []
        for np_str in number_parts:
            val = _parse_number(np_str)
            if val is not None:
                numbers.append(val)

        if len(numbers) >= 4:
            # In the extracted text, reading left to right:
            # [avg] [num_trans] [num_products] [rev_excl_vat] [rev_incl_vat]
            avg_val = numbers[0]
            num_trans = int(numbers[1])
            rev_incl = numbers[-1]
            rev_excl = numbers[-2] if len(numbers) >= 5 else None

            # Validate: rev_incl should be roughly avg * num_trans
            if rev_incl < num_trans:
                sorted_nums = sorted(numbers, reverse=True)
                rev_incl = sorted_nums[0]
                if len(sorted_nums) > 1:
                    rev_excl = sorted_nums[1]
                for n in numbers:
                    if 1 < n < 500 and rev_incl > 0:
                        potential_avg = rev_incl / n
                        if 20 < potential_avg < 150:
                            num_trans = int(n)
                            avg_val = potential_avg
                            break

            # Parse times
            first_time = None
            last_time = None
            if len(times) >= 2:
                t1 = _parse_time(times[-1])
                t2 = _parse_time(times[-2])
                if t1 and t2:
                    first_time = min(t1, t2)
                    last_time = max(t1, t2)
            elif len(times) == 1:
                first_time = _parse_time(times[0])
                last_time = first_time

            results.append({
                "סניף": current_store,
                'מכר כולל מע"מ': rev_incl,
                "ממוצע עסקאות": round(avg_val, 2),
                "מס' עסקאות": num_trans,
                "עסקה ראשונה": first_time,
                "עסקה אחרונה": last_time,
            })

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    if df.empty:
        return df

    # Aggregate: if multiple PDF lines map to the same master branch
    # (e.g. "פלאפל זך" + "מתחם זך" both → רופין), sum revenue &
    # transactions, take min/max times, and recalculate the average.
    agg_dict = {
        'מכר כולל מע"מ': "sum",
        "מס' עסקאות": "sum",
        "עסקה ראשונה": "min",
        "עסקה אחרונה": "max",
        "ממוצע עסקאות": "first",  # placeholder – recalculated below
    }
    df = df.groupby("סניף", as_index=False).agg(agg_dict)
    mask = df["מס' עסקאות"] > 0
    df.loc[mask, "ממוצע עסקאות"] = (
        df.loc[mask, 'מכר כולל מע"מ'] / df.loc[mask, "מס' עסקאות"]
    ).round(2)
    return df


@st.cache_data
def parse_pdf_portions(file_bytes: bytes, file_name: str, target_date: str) -> pd.DataFrame:
    """
    Parse the Paz ארוחות בפיתה PDF (FALAFEL_FOOD).
    For each Paz branch on target_date, extract:
      - מנות בפיתה (= non-meal portions + meals = total)
      - ארוחות בפיתה (= meals)

    target_date: 'DD.MM.YYYY' format
    """
    results = {}

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            all_text = ""
            for page in pdf.pages:
                text = page.extract_text() or ""
                all_text += text + "\n"
    except Exception as e:
        st.warning(f"שגיאה בקריאת PDF מנות: {file_name} - {e}")
        return pd.DataFrame()

    lines = all_text.split("\n")
    in_target_date_block = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        has_date = target_date in line

        # Skip summary lines (האצות = totals)
        if "האצות" in line or "תללוכ" in line:
            if has_date:
                in_target_date_block = True
            continue

        if has_date:
            in_target_date_block = True

        if not has_date and not in_target_date_block:
            continue

        # If we hit a new date, we're out of our block
        date_pattern = r'\d{2}\.\d{2}\.\d{4}'
        dates_in_line = re.findall(date_pattern, line)
        if dates_in_line and target_date not in dates_in_line:
            in_target_date_block = False
            continue

        store = _identify_paz_store(line)
        if store is None:
            continue

        # Extract numbers from the line
        clean = line
        for d in dates_in_line:
            clean = clean.replace(d, " ")

        numbers = re.findall(r'\d+', clean)
        numbers = [int(n) for n in numbers if n.strip()]

        if len(numbers) >= 2:
            total_meals = numbers[0]

            if len(numbers) >= 4:
                non_meal_qty = numbers[-1]
            elif len(numbers) == 3:
                non_meal_qty = numbers[-1]
            else:
                non_meal_qty = numbers[-1]

            total_portions = non_meal_qty + total_meals

            if non_meal_qty < total_meals and len(numbers) > 2:
                candidate = max(numbers)
                if candidate > total_meals:
                    non_meal_qty = candidate
                    total_portions = non_meal_qty + total_meals

            # Accumulate: multiple PDF lines may map to the same master
            # branch (e.g. "פלאפל זך" + "מתחם זך" both → רופין).
            # Sum their portions rather than overwriting.
            if store not in results:
                results[store] = {"total_portions": 0, "meals": 0}
            results[store]["total_portions"] += total_portions
            results[store]["meals"] += total_meals

    rows = []
    for store, data in results.items():
        rows.append({
            "סניף": store,
            "מנות בפיתה": data["total_portions"],
            "ארוחות בפיתה": data["meals"],
        })

    return pd.DataFrame(rows)
