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

## Technical Architecture

The entire app is a single Python file (`app.py`, ~2000 lines) with this structure:

1. **Constants** — branch name mappings, column definitions, display order
2. **File classifier** — auto-detects uploaded file types by content inspection
3. **6 parsers** — one per file type, each returns a normalized pandas DataFrame
4. **Merge engine** — outer-joins all sources into a unified 9-column report
5. **Excel generator** — creates a formatted 2-sheet workbook with openpyxl
6. **Streamlit UI** — sidebar, KPIs, analytics section, charts, data table, download

### Key Technical Details

- **Hebrew RTL**: all sheets, charts, and UI are right-to-left
- **PDF text extraction**: Hebrew characters appear reversed in extracted text. A pattern-matching dictionary handles the mapping.
- **Date filtering**: partner branch PDFs contain cumulative monthly data. The parser extracts only the selected date's row.
- **Encoding detection**: CSVs use an ordered fallback chain (`utf-8-sig → cp1255 → utf-8 → iso-8859-8`) to handle Windows vs. macOS encoding differences.
- **Google Sheets compatibility**: Excel charts use 34-row vertical gaps to prevent overlap when the file is opened in Google Sheets.
- **Dark mode**: all custom HTML uses `rgba()` and `color: inherit` — works in both Streamlit themes.
- **Caching**: all parser functions use `@st.cache_data` to avoid re-parsing on Streamlit reruns.

## Dependencies

```
streamlit>=1.30.0
pandas>=2.0.0
openpyxl>=3.1.0
pdfplumber>=0.10.0
```

No additional dependencies should be added unless strictly necessary.

## Project Structure

```
app.py              — The entire application (single file)
requirements.txt    — Python dependencies (4 packages)
run.bat             — Windows launcher (double-click)
run.command         — macOS launcher (double-click)
.gitignore          — Excludes data files, venv, generated reports
CLAUDE.md           — Internal context file for Claude Code sessions
README.md           — This file
```

## Security & Data Privacy

- The app runs **entirely locally** — no data is sent to any server or cloud service
- All file processing happens in-memory within the local Python process
- Source data files (CSV, Excel, PDF) are excluded from git via `.gitignore`
- Generated Excel reports are excluded from git via `.gitignore`
- No credentials, API keys, or authentication are involved
- The virtual environment is created locally and excluded from git

## Design Decisions

- **Single file**: the app is intentionally kept as one `app.py` file rather than split into modules. The user is non-technical, and a single file is easier to share, backup, and troubleshoot.
- **No database**: all processing is stateless and file-based. There is no persistence between sessions.
- **Minimal dependencies**: only 4 pip packages. No plotly, altair, or other heavy visualization libraries.
- **Defensive parsing**: every parser has try/except blocks and encoding fallbacks. Bad data produces warnings, not crashes.
- **Hebrew-first UI**: every user-facing string is in Hebrew. Error messages explain what went wrong and what to do about it.
