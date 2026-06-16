# Utility Analytics Dashboard for Dialysis Centers

Streamlit dashboard for internal utility analysts managing utility bills across dialysis centers.

## Pages

1. **AI Insights Center / Home** – highest-priority automated insights and financial impact.
2. **Operations Command Center** – portfolio KPIs, top changes, and trend charts.
3. **Exception Center** – sortable/filterable alerts by state, property, utility, and month.
4. **Property Scorecard** – property-level utility trends, billing history, AI explanation, and notes.
5. **Portfolio Benchmarking** – compare centers using cost/treatment and usage/treatment.
6. **Geographic View** – state-level map and geographic drilldown.

## Data Columns Expected

The app is built for your current sheet structure:

- Property Name
- Provider
- Street
- City
- State
- Zip Code
- # Treatments
- Utility
- Meter #
- Unit of Measure
- Acct Number
- Billing Date
- Month
- Year
- Billing Period
- Number Days Billed
- Due Date
- Read period
- Previous Reading
- Current Reading
- Usage
- $ Amount

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Using a Google Sheet

1. Open your Google Sheet.
2. Share it so anyone with the link can view, or publish/export it as CSV.
3. Run the app.
4. In the sidebar, choose **Google Sheet**.
5. Paste the Google Sheet URL.

The app converts standard Google Sheet URLs into CSV export URLs automatically.

## Alert Rules

Default V1 rules:

- **Critical:** cost, usage, or cost/treatment increase greater than 20%.
- **Review:** increase between 10% and 20%.
- **Cost Up / Usage Flat:** possible rate, fee, or billing adjustment.
- **Usage Up / Treatments Flat:** possible leak, meter issue, equipment issue, or unusual operations.
- **Missing/Late Bill:** last bill date is more than 45 days ago.

These thresholds can be changed in `utils/alerts.py`.

## Notes

The analyst notes box currently saves only for the active session. For a production multi-user version, connect notes to Google Sheets, Airtable, Supabase, or another database.
