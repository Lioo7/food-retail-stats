# Daily Sales Reporting Dashboard

A Streamlit web application that automates daily sales reporting for a multi-branch food chain in Israel. It replaces a manual process that previously took ~1.5 hours every morning.

## The Problem

Every day, the business owner had to manually open 7 different data files (CSVs, Excel spreadsheets, and PDFs), copy relevant numbers from each, cross-reference branch names, and paste everything into a master Excel file. This was tedious, error-prone, and took about 90 minutes.

## The Solution

Upload all 7 files into a web dashboard → the app automatically parses, normalizes branch names, merges the data, and produces both an interactive dashboard and a downloadable formatted Excel report — in under 10 seconds.

## Who Uses This

A single non-technical business owner who operates 24 branches. He runs the app once per day on either Windows or macOS. He has no programming experience and should never need to open a terminal, edit code, or configure anything.

## Features

- Drag-and-drop upload for all 7 source files (CSV, Excel, PDF)
- Automatic file type detection and parsing
- Missing file detection with clear warnings (in Hebrew)
- Interactive dashboard with KPI cards, analytics tables, and 4 chart types
- Branch ranking table with top 3 / bottom 3 highlighting
- Revenue efficiency metrics (revenue per operating hour)
- Group comparison (chain branches vs. partner branches)
- Downloadable 2-sheet Excel report with professional formatting and embedded charts
- Works in both light and dark mode
- Cross-platform: runs on both Windows and macOS
- Optional password protection for cloud deployments

## Quick Start

### On macOS

1. Make sure Python 3.8+ is installed
2. Double-click `run.command` (first time: run `chmod +x run.command` in Terminal)
3. The dashboard opens automatically in your browser at `http://localhost:8501`

### On Windows

1. Make sure Python 3.8+ is installed and in your PATH
2. Double-click `run.bat`
3. The dashboard opens automatically in your browser at `http://localhost:8501`

Both launchers automatically create a virtual environment and install dependencies on first run.

### Manual Setup

```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# or: venv\Scripts\activate     # Windows
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

## Password Protection (Optional)

For cloud deployments (e.g., Streamlit Community Cloud), you can add a password gate:

1. Create a file at `.streamlit/secrets.toml`
2. Add the following line:
   ```toml
   password = "your-secret-password"
   ```
3. The file is gitignored and will never be committed.

When no secret is configured (typical for local use), the password gate is skipped entirely — no setup needed.

On Streamlit Community Cloud, add the secret via the app settings UI instead of a local file.

## Input Files (7 per day)

| # | Format | Contains |
|---|--------|----------|
| 1 | CSV | Gross revenue per branch (incl. VAT) |
| 2 | Excel | Average transaction value + transaction count |
| 3 | Excel | Pita portion counts + meal counts |
| 4 | Excel | Hourly transaction data (first/last transaction times) |
| 5–6 | PDF | Partner branch sales data (1–2 files, cumulative monthly) |
| 7 | PDF | Partner branch portion + meal data |

The app auto-detects which file is which — no need to name them in any specific way.

## Output

### Interactive Dashboard

- **Hero KPI**: total daily revenue (the most important number, displayed prominently)
- **Secondary KPIs**: total transactions, total portions, top branch, active branch count
- **Group split**: chain vs. partner revenue share
- **Ranking table**: all branches sorted by revenue with derived metrics (operating hours, revenue/hour, meal conversion rate). Top 3 highlighted in gold, bottom 3 in red.
- **4 chart tabs**: revenue by branch, revenue per hour, portions & meals, meal upsell %
- **Full data table**: all 24 branches with 9 columns

### Excel Report (2 sheets)

- **Sheet 1**: daily report matching the legacy master file format — title bar, headers, data, totals row, formatting, freeze panes, print-ready
- **Sheet 2 ("ניתוח")**: analytics — branch ranking table, group summary, 4 embedded charts

## Project Structure

```
app.py              — Entry point: auth → sidebar → process files → render dashboard
config.py           — Shared constants (branch maps, columns, display order)
auth.py             — Optional password gate using st.secrets

parsers/            — File classification and parsing
  classifier.py     — Auto-detects uploaded file type
  csv_parser.py     — CSV revenue parser
  excel_parser.py   — 3 Excel parsers (avg transactions, portions, hourly)
  pdf_parser.py     — 2 PDF parsers (Paz sales + portions)

logic/              — Business logic
  merge.py          — Branch name normalization + multi-source merge

export/             — Report generation
  excel_export.py   — 2-sheet formatted Excel with charts

ui/                 — Streamlit UI components
  styles.py         — Theme-aware CSS
  sidebar.py        — Sidebar rendering
  kpi_cards.py      — KPI card rendering
  analytics.py      — Analytics section (rankings, summaries)
  charts.py         — 4 chart tabs
  data_table.py     — Data table + debug expander

requirements.txt    — Python dependencies (4 packages)
run.bat             — Windows launcher (double-click)
run.command         — macOS launcher (double-click)
```

## Dependencies

```
streamlit>=1.30.0
pandas>=2.0.0
openpyxl>=3.1.0
pdfplumber>=0.10.0
```

No additional dependencies should be added unless strictly necessary.

## Security & Data Privacy

- The app runs **entirely locally** — no data is sent to any server or cloud service
- All file processing happens in-memory within the local Python process
- Source data files (CSV, Excel, PDF) are excluded from git via `.gitignore`
- Generated Excel reports are excluded from git via `.gitignore`
- The optional password gate uses `st.secrets` (gitignored)
- The virtual environment is created locally and excluded from git

## Technical Details

- **Hebrew RTL**: all sheets, charts, and UI are right-to-left
- **PDF text extraction**: Hebrew characters appear reversed in extracted text. A pattern-matching dictionary handles the mapping.
- **Date filtering**: partner branch PDFs contain cumulative monthly data. The parser extracts only the selected date's row.
- **Encoding detection**: CSVs use an ordered fallback chain (`utf-8-sig → cp1255 → utf-8 → iso-8859-8`) to handle Windows vs. macOS encoding differences.
- **Google Sheets compatibility**: Excel charts use 34-row vertical gaps to prevent overlap when the file is opened in Google Sheets.
- **Dark mode**: all custom HTML uses `rgba()` and `color: inherit` — works in both Streamlit themes.
- **Caching**: all parser functions use `@st.cache_data` to avoid re-parsing on Streamlit reruns.
