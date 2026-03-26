"""Theme-aware CSS for the dashboard."""

import streamlit as st

CSS = """
<style>
/* ── KPI Cards ── */
.kpi-hero {
    background: linear-gradient(135deg, #4472C4 0%, #2F5496 100%);
    padding: 1.6rem 1rem;
    border-radius: 14px;
    color: #ffffff;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
.kpi-hero h3 { font-size: 1rem; margin: 0 0 0.3rem 0; opacity: 0.9; }
.kpi-hero h1 { font-size: 2.8rem; margin: 0; font-weight: 800; }
.kpi-card {
    padding: 1rem;
    border-radius: 12px;
    color: #ffffff;
    text-align: center;
    box-shadow: 0 3px 12px rgba(0,0,0,0.15);
}
.kpi-card h3 { font-size: 0.85rem; margin: 0 0 0.2rem 0; opacity: 0.9; }
.kpi-card h1 { font-size: 1.8rem; margin: 0; font-weight: 700; }
.kpi-card p  { font-size: 0.85rem; margin: 0.2rem 0 0 0; opacity: 0.85; }
.kpi-green  { background: linear-gradient(135deg, #0d9373 0%, #2ab77b 100%); }
.kpi-orange { background: linear-gradient(135deg, #e0842b 0%, #e8b32a 100%); }
.kpi-blue   { background: linear-gradient(135deg, #1e87a0 0%, #5bbfd4 100%); }
.kpi-purple { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }

/* ── Section Headers ── */
.section-hdr {
    font-size: 1.3rem;
    font-weight: 700;
    margin: 1.5rem 0 0.6rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 3px solid #4472C4;
}

/* ── Group split cards (Paz vs Chain) ── */
.grp-card {
    padding: 1.2rem 0.8rem;
    border-radius: 12px;
    text-align: center;
    border: 2px solid;
}
.grp-card h4 { font-size: 0.9rem; margin: 0 0 0.2rem 0; opacity: 0.7; }
.grp-card h2 { font-size: 1.8rem; margin: 0.2rem 0; font-weight: 700; }
.grp-card p  { font-size: 1rem; margin: 0; opacity: 0.7; }
.grp-chain {
    border-color: #4472C4;
    background: rgba(68,114,196,0.12);
    color: inherit;
}
.grp-paz {
    border-color: #F2994A;
    background: rgba(242,153,74,0.12);
    color: inherit;
}

/* ── Download Button ── */
.stDownloadButton > button {
    width: 100%;
    background-color: #4CAF50 !important;
    color: white !important;
    font-size: 1.2rem !important;
    padding: 0.7rem !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: bold !important;
}
.stDownloadButton > button:hover {
    background-color: #45a049 !important;
}
</style>
"""


def inject_css():
    """Inject theme-aware CSS into the page."""
    st.markdown(CSS, unsafe_allow_html=True)
