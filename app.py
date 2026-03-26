"""
Falafel Bribua - Daily Sales Reporting Dashboard
=================================================
Streamlit app that aggregates data from multiple sources (CSV, Excel, PDF)
into a unified daily report matching the master file format.
"""

import streamlit as st

from auth import check_password
from parsers import (
    classify_file,
    parse_csv_revenue,
    parse_xlsx_avg_trans,
    parse_xlsx_portions,
    parse_xlsx_hourly,
    parse_pdf_sales,
    parse_pdf_portions,
)
from logic import merge_all
from export import generate_excel
from ui.styles import inject_css
from ui.sidebar import render_sidebar
from ui.kpi_cards import render_kpi_cards
from ui.analytics import render_analytics
from ui.charts import render_charts
from ui.data_table import render_data_table, render_debug

# ──────────────────────────────────────────────
# Page config (must be the first Streamlit call)
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="פלאפל בריבוע - דוח יומי",
    page_icon="🧆",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    # ── Authentication gate ──
    if not check_password():
        return

    # ── Inject CSS ──
    inject_css()

    # ── Sidebar ──
    report_date, uploaded_files, sidebar_download_placeholder = render_sidebar()

    # ── Main area ──
    st.markdown("## 📊 דוח מכירות יומי — פלאפל בריבוע")

    if not uploaded_files:
        st.info(
            "👈 העלה קבצים בסרגל הצד כדי להתחיל.\n\n"
            "**קבצים נדרשים (7):**\n"
            "- 🟢 CSV מכר כולל מע\"מ\n"
            "- 🟢 Excel ממוצע עסקה + מס' עסקאות\n"
            "- 🟢 Excel סה\"כ מנות מול ארוחה בפיתה\n"
            "- 🟢 Excel עסקאות לפי שעה\n"
            "- 🟠 PDF מכירות חנות — פז (1-2 קבצים)\n"
            "- 🟠 PDF ארוחות בפיתה — פז"
        )
        return

    # ── Process files ──
    target_date_str = report_date.strftime("%d.%m.%Y")

    csv_data = None
    avg_trans_data = None
    portions_data = None
    hourly_data = None
    paz_sales_list = []
    paz_portions_list = []
    file_classifications = {}

    for f in uploaded_files:
        file_bytes = f.read()
        f.seek(0)
        ftype = classify_file(f.name, file_bytes)
        file_classifications[f.name] = ftype

        try:
            if ftype == "csv_revenue":
                csv_data = parse_csv_revenue(file_bytes, f.name)
            elif ftype == "xlsx_avg_trans":
                avg_trans_data = parse_xlsx_avg_trans(file_bytes, f.name)
            elif ftype == "xlsx_portions":
                portions_data = parse_xlsx_portions(file_bytes, f.name)
            elif ftype == "xlsx_hourly":
                hourly_data = parse_xlsx_hourly(file_bytes, f.name)
            elif ftype == "pdf_sales":
                result = parse_pdf_sales(file_bytes, f.name, target_date_str)
                if result is not None and not result.empty:
                    paz_sales_list.append(result)
            elif ftype == "pdf_portions":
                result = parse_pdf_portions(file_bytes, f.name, target_date_str)
                if result is not None and not result.empty:
                    paz_portions_list.append(result)
            else:
                st.warning(f"⚠️ לא הצלחתי לזהות את סוג הקובץ: {f.name}")
        except Exception as e:
            st.error(f"❌ שגיאה בעיבוד {f.name}: {e}")

    # ── File completeness checklist ──
    _detected_types = set(file_classifications.values())
    _pdf_sales_count = sum(1 for v in file_classifications.values() if v == "pdf_sales")
    _checklist = [
        ("csv_revenue", "CSV מכר כולל מע\"מ"),
        ("xlsx_avg_trans", "Excel ממוצע עסקה"),
        ("xlsx_portions", "Excel מנות בפיתה"),
        ("xlsx_hourly", "Excel עסקאות לפי שעה"),
        ("pdf_sales", f"PDF מכירות פז ({_pdf_sales_count} קבצים)"),
        ("pdf_portions", "PDF מנות פז"),
    ]
    _missing = [label for ftype, label in _checklist if ftype not in _detected_types]
    if _missing:
        st.warning("⚠️ **קבצים חסרים:** " + " · ".join(_missing))

    type_labels = {
        "csv_revenue": "CSV מכר כולל מע\"מ",
        "xlsx_avg_trans": "Excel ממוצע עסקה",
        "xlsx_portions": "Excel מנות בפיתה",
        "xlsx_hourly": "Excel עסקאות לפי שעה",
        "pdf_sales": "PDF מכירות חנות (פז)",
        "pdf_portions": "PDF ארוחות בפיתה (פז)",
        "unknown": "❓ לא ידוע",
    }

    with st.expander("🔍 זיהוי קבצים", expanded=bool(_missing)):
        for ftype, label in _checklist:
            icon = "✅" if ftype in _detected_types else "❌"
            st.markdown(f"{icon} {label}")
        st.divider()
        for fname, ftype in file_classifications.items():
            st.write(f"**{fname}** → {type_labels.get(ftype, ftype)}")

    # ── Merge ──
    try:
        merged = merge_all(
            csv_data, avg_trans_data, portions_data, hourly_data,
            paz_sales_list, paz_portions_list,
        )
    except Exception as e:
        st.error(f"❌ שגיאה במיזוג הנתונים: {e}")
        return

    if merged.empty:
        st.warning("לא נמצאו נתונים לתאריך הנבחר. ודא שהקבצים תואמים את התאריך.")
        return

    # ── Toast: report ready ──
    st.toast("✅ הדוח מוכן!", icon="🧆")

    # ── Download buttons (above tabs — always visible) ──
    excel_bytes = generate_excel(merged, report_date)
    date_str = report_date.strftime("%d.%m.%y")
    file_name = f"דוח_יומי_{date_str}.xlsx"

    with sidebar_download_placeholder:
        st.divider()
        st.download_button(
            label=f"⬇️ הורד דוח יומי - {report_date.strftime('%d/%m/%Y')}",
            data=excel_bytes,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="sidebar_download",
        )

    st.download_button(
        label=f"⬇️ הורד דוח יומי - {report_date.strftime('%d/%m/%Y')}",
        data=excel_bytes,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="main_download",
    )

    # ── Tabbed navigation ──
    tab_dashboard, tab_charts, tab_data = st.tabs([
        "📊 דשבורד מרכזי",
        "📈 גרפים ומגמות",
        "📋 נתונים מלאים",
    ])

    # Compute ranking_df outside tabs so it's available to both dashboard and charts
    ranking_df = None

    with tab_dashboard:
        render_kpi_cards(merged)
        ranking_df = render_analytics(merged)

    with tab_charts:
        if ranking_df is not None:
            render_charts(merged, ranking_df)

    with tab_data:
        render_data_table(merged)
        render_debug(csv_data, avg_trans_data, portions_data, hourly_data,
                     paz_sales_list, paz_portions_list)


if __name__ == "__main__":
    main()
