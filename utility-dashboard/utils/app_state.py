from __future__ import annotations

import streamlit as st

from utils.alerts import build_alerts
from utils.calculations import monthly_summary
from utils.data_loader import load_data


def data_source_sidebar() -> tuple[str, str | None, object | None]:
    """Render the shared data-source controls used by every page."""
    st.sidebar.markdown("# 📊 Utility Analytics")
    st.sidebar.markdown("for Dialysis Centers")
    st.sidebar.divider()
    st.sidebar.caption("Live mode: Google Sheets reloads on every page refresh/rerun.")

    default_url = ""
    try:
        default_url = st.secrets.get("GOOGLE_SHEET_URL", "")
    except Exception:
        default_url = ""

    source = st.sidebar.radio(
        "Data Source",
        ["Google Sheet", "Sample Excel", "Upload Excel/CSV"],
        index=0,
        key="data_source",
    )
    google_sheet_url = None
    uploaded_file = None

    if source == "Google Sheet":
        google_sheet_url = st.sidebar.text_input(
            "Google Sheet share link or CSV export URL",
            value=st.session_state.get("google_sheet_url", default_url),
            key="google_sheet_url",
        )
        st.sidebar.caption("The sheet must be shared as viewable or published to the web.")
        if st.sidebar.button("Refresh Google Sheet now", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    elif source == "Upload Excel/CSV":
        uploaded_file = st.sidebar.file_uploader("Upload Property Excel/CSV", type=["xlsx", "xls", "csv"])

    return source, google_sheet_url, uploaded_file


def load_current_data():
    """Load fresh data and store the normalized raw, monthly, and alerts dataframes."""
    source, google_sheet_url, uploaded_file = data_source_sidebar()

    try:
        df = load_data(source, google_sheet_url, uploaded_file)
    except Exception as exc:
        st.error(f"Could not load data: {exc}")
        if source == "Google Sheet":
            st.info("Check that the Google Sheet link is shared as viewable. For the most reliable setup, use File → Share → Publish to web → CSV, then paste that CSV link.")
        st.stop()

    monthly = monthly_summary(df)
    alerts = build_alerts(monthly)
    st.session_state["raw_df"] = df
    st.session_state["monthly"] = monthly
    st.session_state["alerts"] = alerts
    return df, monthly, alerts
