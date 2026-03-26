# CLAUDE.md — Project Context for Claude Code

> This file gives Claude the full context needed to work on this project
> without re-reading every line of code. Read this first on every new session.

---

## 1. What Is This Project?

A **Streamlit daily sales reporting dashboard** for a 24-branch Israeli food chain.
It replaces a **manual 1.5-hour daily process** where the owner copied data from
CSVs, Excel files, and PDFs into a master Excel spreadsheet by hand.

The app: upload 7 source files → auto-merge → view dashboard → download formatted Excel.

## 2. Who Is the User?

**Lio** — the business owner. He is **non-technical** (not a developer).
He runs this once a day, every morning. He works on **both macOS and Windows**.
He should never need to open a terminal, edit code, or touch config files.
All visible UI text is in **Hebrew (RTL)**.

## 3. Project Files

```
app.py              — Lightweight entry point (~170 lines): auth → sidebar → process → render
config.py           — Shared constants (branch maps, column definitions, display order)
auth.py             — Password gate using st.secrets (optional, skipped when unconfigured)

parsers/            — File classification and parsing
  __init__.py       — Re-exports all parser functions
  classifier.py     — Auto-detects uploaded file type by content inspection
  csv_parser.py     — CSV revenue parser (column D, encoding fallback chain)
  excel_parser.py   — 3 Excel parsers (avg transactions, portions, hourly)
  pdf_parser.py     — 2 PDF parsers (Paz sales + portions) + PAZ_STORE_PATTERNS

logic/              — Business logic
  __init__.py       — Re-exports normalize_branch, merge_all
  merge.py          — Branch name normalization + multi-source outer-join merge

export/             — Report generation
  __init__.py       — Re-exports generate_excel
  excel_export.py   — 2-sheet formatted Excel with charts (CHART_GAP = 34)

ui/                 — Streamlit UI components
  __init__.py
  styles.py         — Theme-aware CSS (dark mode safe)
  sidebar.py        — Sidebar: branding, date picker, file uploader
  kpi_cards.py      — Hero revenue card + 4 secondary KPI cards
  analytics.py      — Paz vs Chain split, ranking table, summary table
  charts.py         — 4 chart tabs (revenue, efficiency, portions, meal %)
  data_table.py     — Formatted data table + debug expander

requirements.txt    — 4 deps: streamlit, pandas, openpyxl, pdfplumber
run.bat             — Windows double-click launcher (creates venv, installs deps, runs)
run.command         — macOS double-click launcher (same flow, bash)
.gitignore          — Excludes data files, venv, secrets, preview xlsx
CLAUDE.md           — This file
README.md           — User/developer facing documentation
```

## 4. Architecture

### Constants (`config.py`)
- `BRANCH_NAME_MAP` — dict mapping raw source names → canonical master names
- `PAZ_BRANCHES` — set of 7 branch names that come from PDF sources (gas-station partnership)
- `MASTER_COLUMNS` — the 9 columns in the output report
- `MASTER_BRANCH_ORDER` — fixed display order (17 chain + 7 partner = 24 branches)

### Parsers (`parsers/`)
Each returns a DataFrame with a `סניף` (branch) column:

| Function | Input | Extracts |
|----------|-------|----------|
| `parse_csv_revenue` | CSV | gross revenue per branch (column D "בחירת מדד") |
| `parse_xlsx_avg_trans` | Excel | avg transaction + transaction count |
| `parse_xlsx_portions` | Excel | pita portions + meals count |
| `parse_xlsx_hourly` | Excel | first/last transaction times |
| `parse_pdf_sales` | PDF | Paz branch revenue, transactions, times for a specific date |
| `parse_pdf_portions` | PDF | Paz branch pita portions + meals for a specific date |

**All parsers are decorated with `@st.cache_data`** to avoid re-parsing on Streamlit reruns.

### Business Logic (`logic/merge.py`)
- `normalize_branch(name)` — maps any raw name to master name via `BRANCH_NAME_MAP`
- `merge_all(...)` — outer-joins all 6 data sources into one DataFrame
- Paz data overwrites/appends to the merged frame
- Calculates meal percentage
- Sorts by `MASTER_BRANCH_ORDER`

### Excel Export (`export/excel_export.py`)
- `generate_excel(df, report_date)` — creates a 2-sheet .xlsx in memory
  - **Sheet 1** ("DD.M"): the main daily report with 9 columns, totals row, formatting
  - **Sheet 2** ("ניתוח"): analytics — ranking table, Paz vs chain summary, 4 charts
- Charts use `CHART_GAP = 34` rows between anchors (Google Sheets compatibility fix)
- Helper data for charts is written to column 14+ (offscreen)

### Streamlit UI (`ui/`)
Rendered in this order by `app.py`:
1. **Auth gate** (`auth.py`): password check (skipped if no secret configured)
2. **CSS** (`ui/styles.py`): theme-aware styles
3. **Sidebar** (`ui/sidebar.py`): branding → date picker → file uploader → download button
4. **File checklist**: warns if required files are missing, shows ✅/❌ per type
5. **KPI cards** (`ui/kpi_cards.py`): hero revenue card (full width) + 4 secondary cards
6. **Analytics** (`ui/analytics.py`): Paz vs Chain split, ranking table, summary table
7. **Charts** (`ui/charts.py`): 4 chart tabs
8. **Data table** (`ui/data_table.py`): full merged data + debug expander
9. **Download buttons**: sidebar + main area

## 5. The 7 Input Files

The user uploads 7 files every day:

| # | Type | Description |
|---|------|-------------|
| 1 | CSV | Revenue per branch (gross incl. VAT) — **column D**, not E |
| 2 | Excel | Average transaction value + transaction count |
| 3 | Excel | Pita portions vs meals count |
| 4 | Excel | Hourly transactions (first/last time) |
| 5 | PDF | Partner-branch sales (may be 1 or 2 PDFs) |
| 6 | PDF | Partner-branch sales (second PDF, if exists) |
| 7 | PDF | Partner-branch pita portions + meals |

### CSV Gotcha (Bug Fix History)
Column E header says "כולל מע"מ" but has WRONG values. The correct gross revenue
is in **column D** ("בחירת מדד"). The parser explicitly targets column D.

### PDF Gotcha (Bug Fix History)
Hebrew text in PDFs from printed Gmail emails appears **reversed** at the character level.
For example, "מתחם זך" → "ךז םחתמ". The `PAZ_STORE_PATTERNS` dict maps reversed
patterns to master branch names. **Longer patterns must come before shorter ones.**

### Branch Aggregation Gotcha (Bug Fix History)
Some partner branches have multiple lines in PDFs that map to the same master branch.
For example, "פלאפל זך" and "מתחם זך" both map to "רופין".
The parsers **sum** (not replace) when multiple lines map to the same branch.

## 6. The 9 Output Columns

```
סניף                    — Branch name (canonical)
מכר כולל מע"מ           — Gross revenue including VAT
ממוצע עסקאות            — Average transaction value
מס' עסקאות              — Number of transactions
עסקה ראשונה             — First transaction time (datetime.time)
עסקה אחרונה             — Last transaction time (datetime.time)
מנות בפיתה              — Total pita items (includes meals)
ארוחות בפיתה            — Meals in pita (subset of מנות)
אחוז ארוחות מתוך מנות   — Meal percentage (calculated)
```

## 7. Two Branch Groups

- **Chain branches** (17): data comes from CSV + Excel files
- **Partner branches** (7, listed in `PAZ_BRANCHES`): data comes from PDFs, which contain
  **cumulative monthly data** requiring date filtering via `target_date`

## 8. Cross-Platform Concerns

- CSV encoding: ordered fallback chain `utf-8-sig → cp1255 → utf-8 → iso-8859-8`
- Path separators: all use `pathlib` or forward slashes
- Launchers: `run.bat` for Windows, `run.command` for macOS (both create venv automatically)

## 9. Authentication

- Uses `st.secrets["password"]` for optional password protection
- When no secret is configured (local use), access is granted automatically
- Setup: create `.streamlit/secrets.toml` with `password = "your-password"`
- The secrets file is gitignored

## 10. Dark Mode

All custom HTML uses `rgba()` backgrounds and `color: inherit` — no hardcoded
light-mode text colors. Cards use white text on gradient backgrounds.

## 11. Excel Export Structure

### Sheet 1 (data sheet, named by day e.g. "25.3"):
- Row 1: merged title bar with date
- Row 2: blue column headers
- Row 3+: data with zebra striping
- Totals row with border separation
- Freeze panes at A3, RTL, print-ready

### Sheet 2 ("ניתוח"):
- Section A: Branch ranking table with derived columns (rank, %, hours, revenue/hr)
- Section B: Chain vs Partner group summary
- Section C: 4 charts stacked vertically with 34-row gaps (Google Sheets compat)

## 12. Known Bugs That Were Fixed (Don't Re-Introduce)

1. **CSV column bug**: NEVER use column E for revenue. Always use column D ("בחירת מדד").
2. **Reversed Hebrew in PDFs**: `PAZ_STORE_PATTERNS` handles this. Don't simplify the dict.
3. **Branch aggregation**: Multiple PDF lines → same branch must SUM, not overwrite.
4. **Chart overlap in Google Sheets**: Charts need `CHART_GAP = 34` rows between anchors.
5. **Dark mode text**: Never use hardcoded dark text colors in custom HTML.

## 13. Rules for Future Changes

- **Do NOT add new pip dependencies** unless absolutely necessary and approved by the user.
- **Do NOT modify parsing logic** when making UI changes (and vice versa).
- **All user-facing text must be in Hebrew.**
- **Test on both light and dark Streamlit themes.**
- The user is non-technical — error messages must be actionable and in Hebrew.
- Always keep the `@st.cache_data` decorators on parser functions.
- When modifying a module, keep changes scoped to that module's responsibility.
