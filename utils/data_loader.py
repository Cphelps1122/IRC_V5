from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

REQUIRED_COLUMNS = [
    "Property Name", "Provider", "City", "State", "# Treatments", "Utility",
    "Billing Date", "Month", "Year", "Number Days Billed", "Usage", "$ Amount"
]

COLUMN_ALIASES = {
    "Property": "Property Name",
    "PropertyName": "Property Name",
    "Property Name ": "Property Name",
    "Treatments": "# Treatments",
    "Treatment Count": "# Treatments",
    "Amount": "$ Amount",
    "Cost": "$ Amount",
    "Dollar Amount": "$ Amount",
    "BillingDate": "Billing Date",
    "Days Billed": "Number Days Billed",
}


def google_sheet_to_csv_url(url: str) -> str:
    """Convert a Google Sheet share URL to a CSV export URL."""
    if "docs.google.com/spreadsheets" not in url:
        return url
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if not match:
        return url
    gid_match = re.search(r"gid=([0-9]+)", url)
    gid = gid_match.group(1) if gid_match else "0"
    sheet_id = match.group(1)
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns={k: v for k, v in COLUMN_ALIASES.items() if k in df.columns})
    return df


def normalize_data(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.warning(f"Missing expected columns: {', '.join(missing)}. Some dashboard sections may be limited.")

    for col in ["Billing Date", "Due Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["# Treatments", "Number Days Billed", "Usage", "$ Amount", "Previous Reading", "Current Reading"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Billing Date" in df.columns:
        df["Bill Month"] = df["Billing Date"].dt.to_period("M").dt.to_timestamp()
    elif {"Month", "Year"}.issubset(df.columns):
        df["Bill Month"] = pd.to_datetime(df["Month"].astype(str) + " " + df["Year"].astype(str), errors="coerce")
    else:
        df["Bill Month"] = pd.NaT

    for col in ["Property Name", "Provider", "City", "State", "Utility", "Unit of Measure"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    df["Cost per Treatment"] = df["$ Amount"] / df["# Treatments"].replace({0: pd.NA}) if {"$ Amount", "# Treatments"}.issubset(df.columns) else pd.NA
    df["Usage per Treatment"] = df["Usage"] / df["# Treatments"].replace({0: pd.NA}) if {"Usage", "# Treatments"}.issubset(df.columns) else pd.NA
    df["Cost per Day"] = df["$ Amount"] / df["Number Days Billed"].replace({0: pd.NA}) if {"$ Amount", "Number Days Billed"}.issubset(df.columns) else pd.NA
    df["Usage per Day"] = df["Usage"] / df["Number Days Billed"].replace({0: pd.NA}) if {"Usage", "Number Days Billed"}.issubset(df.columns) else pd.NA
    return df


@st.cache_data(show_spinner=False)
def load_excel(path: str | Path, sheet_name: str = "Property") -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet_name)
    return normalize_data(df)


@st.cache_data(show_spinner=False, ttl=600)
def load_google_sheet(url: str) -> pd.DataFrame:
    csv_url = google_sheet_to_csv_url(url)
    df = pd.read_csv(csv_url)
    return normalize_data(df)


def load_data(source: str = "Sample Excel", google_sheet_url: Optional[str] = None, uploaded_file=None) -> pd.DataFrame:
    if source == "Google Sheet" and google_sheet_url:
        return load_google_sheet(google_sheet_url)
    if source == "Upload Excel/CSV" and uploaded_file is not None:
        if uploaded_file.name.lower().endswith(".csv"):
            return normalize_data(pd.read_csv(uploaded_file))
        return normalize_data(pd.read_excel(uploaded_file, sheet_name="Property"))
    return load_excel(Path(__file__).resolve().parents[1] / "data" / "sample_irc_database.xlsx")
