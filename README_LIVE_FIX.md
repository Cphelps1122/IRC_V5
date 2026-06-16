# Live Google Sheet Fix

This version removes the fragile requirement to use `.streamlit/secrets.toml` for local testing.

## One-time setup

Open `config.py` and paste your Google Sheet link once:

```python
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit?gid=0#gid=0"
GOOGLE_WORKSHEET = "Property"
AUTO_REFRESH_SECONDS = 30
```

Then run the app from the same folder that contains `app.py` and `config.py`:

```bash
streamlit run app.py
```

The dashboard will auto-refresh every 30 seconds and pull the current Google Sheet CSV each time.

## Important

Your sheet must be set to **Anyone with the link can view**.

If your data is not on the first tab, paste the full Google Sheet URL with the correct `gid=` value or set `GOOGLE_SHEET_GID` in `config.py`.
