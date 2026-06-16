"""
Utility Dashboard connection settings.

Set your Google Sheet ONCE here. After that, the dashboard reads it live.

Use either GOOGLE_SHEET_URL or GOOGLE_SHEET_ID.
For a sheet that is "Anyone with the link can view", no service account is needed.
"""

DATA_SOURCE = "Google Sheet"

# Paste your full Google Sheet URL here one time.
# Example:
# GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1abc123YourSheetId/edit?gid=0#gid=0"
GOOGLE_SHEET_URL = ""

# Or paste only the spreadsheet ID here instead.
GOOGLE_SHEET_ID = "1_4coHOmEkzY9cLYRtqmnUJ51LuqeY6yz"

# Your worksheet/tab name from the bottom of Google Sheets.
GOOGLE_WORKSHEET = "Property"

# The tab gid. If your full URL includes gid=..., the app can read it automatically.
# Keep this as "0" unless your data is on a different tab and you are using GOOGLE_SHEET_ID only.
GOOGLE_SHEET_GID = "0"

# How often Streamlit auto-refreshes the dashboard.
AUTO_REFRESH_SECONDS = 30
