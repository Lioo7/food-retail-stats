"""Auto-detect uploaded file type by inspecting content."""

import io
import pandas as pd
import pdfplumber


def classify_file(file_name: str, file_bytes: bytes) -> str:
    """
    Classify uploaded file into one of:
      'csv_revenue'       – מכר כולל מעמ.csv
      'xlsx_avg_trans'     – ממוצע עסקה+מס' עסקאות.xlsx
      'xlsx_portions'      – סהכ מנות מול ארוחה בפיתה.xlsx
      'xlsx_hourly'        – עסקאות לפי שעה.xlsx
      'pdf_sales'          – מכירות חנות PDF (Paz revenue)
      'pdf_portions'       – ארוחות בפיתה PDF (Paz portions)
      'unknown'
    """
    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""

    if ext == "csv":
        return "csv_revenue"

    if ext in ("xlsx", "xls"):
        try:
            df = pd.read_excel(io.BytesIO(file_bytes), header=None, nrows=5)
            text = " ".join(str(v) for v in df.values.flatten() if pd.notna(v))
            if "ממוצע להזמנה" in text or "ממוצע" in text and "הזמנות" in text:
                return "xlsx_avg_trans"
            if "תמחור" in text or "ארוחה בפיתה" in text:
                return "xlsx_portions"
            if "סה\"כ" in text and ("מכירות כולל" in text or "הזמנות" in text):
                return "xlsx_hourly"
            # Fallback: check more rows
            df_full = pd.read_excel(io.BytesIO(file_bytes), header=None, nrows=20)
            text_full = " ".join(str(v) for v in df_full.values.flatten() if pd.notna(v))
            if "ממוצע" in text_full:
                return "xlsx_avg_trans"
            if "תמחור" in text_full or "נמכר" in text_full:
                return "xlsx_portions"
            return "xlsx_hourly"
        except Exception:
            return "unknown"

    if ext == "pdf":
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                first_page_text = pdf.pages[0].extract_text() or ""
                if "FALAFEL_FOOD" in first_page_text or "התיפב תוחורא" in first_page_text:
                    return "pdf_portions"
                if "תוריכמ" in first_page_text or "ןוידפ" in first_page_text:
                    return "pdf_sales"
                if any(c.isdigit() for c in first_page_text[:200]):
                    return "pdf_sales"
        except Exception:
            pass
        return "unknown"

    return "unknown"
