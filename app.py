from __future__ import annotations
import streamlit as st
from utils.data_loader import load_data
from utils.calculations import monthly_summary, latest_month, money_fmt, num_fmt
from utils.alerts import build_alerts
from utils.ui import apply_css, metric_card
from utils.charts import line

st.set_page_config(page_title="Utility Analytics", page_icon="📊", layout="wide")
apply_css()

st.sidebar.markdown("# 📊 Utility Analytics")
st.sidebar.markdown("for Dialysis Centers")
st.sidebar.divider()
source = st.sidebar.radio("Data Source", ["Sample Excel", "Google Sheet", "Upload Excel/CSV"], index=0)
gsheet = None; upload = None
if source == "Google Sheet":
    gsheet = st.sidebar.text_input("Google Sheet share link or CSV export URL")
    st.sidebar.caption("Share the sheet as viewable, then paste the link here.")
elif source == "Upload Excel/CSV":
    upload = st.sidebar.file_uploader("Upload Property Excel/CSV", type=["xlsx", "xls", "csv"])

try:
    df = load_data(source, gsheet, upload)
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

monthly = monthly_summary(df)
alerts = build_alerts(monthly)
st.session_state["raw_df"] = df
st.session_state["monthly"] = monthly
st.session_state["alerts"] = alerts

st.title("AI Insights Center")
st.caption("Start here each morning: highest-impact utility changes, anomalies, and review priorities.")

lm = latest_month(monthly)
current = monthly[monthly["Bill Month"] == lm] if lm is not None else monthly
alert_current = alerts[alerts["Bill Month"] == lm] if lm is not None else alerts

c1,c2,c3,c4,c5 = st.columns(5)
with c1: metric_card("Total Portfolio Cost", money_fmt(current["Total_Cost"].sum()))
with c2: metric_card("Total Usage", num_fmt(current["Total_Usage"].sum()))
with c3: metric_card("Avg Cost / Treatment", f"${current['Cost_per_Treatment'].mean():,.2f}" if len(current) else "—")
with c4: metric_card("Critical Insights", str((alert_current["Alert Level"]=="Critical").sum()))
with c5: metric_card("Est. Monthly Impact", money_fmt(alert_current["Estimated Monthly Impact"].sum()))

st.subheader("Priority Insights")
insights = alert_current.sort_values(["Alert Level", "Estimated Monthly Impact"], ascending=[True, False]).copy()
if not insights.empty:
    from utils.alerts import generate_insight
    insights["Insight"] = insights.apply(generate_insight, axis=1)
    show = insights[["Alert Level","Property Name","State","Utility","Alert Type","Insight","Estimated Monthly Impact","Last_Bill_Date"]].head(20)
    st.dataframe(show, use_container_width=True, hide_index=True)
else:
    st.info("No current insights available yet.")

st.subheader("Portfolio Trends")
trend = monthly.groupby("Bill Month", as_index=False).agg(Total_Cost=("Total_Cost","sum"), Total_Usage=("Total_Usage","sum"), Treatments=("Treatments","sum"))
a,b = st.columns(2)
with a: st.plotly_chart(line(trend, "Bill Month", "Total_Cost", "Total Portfolio Cost"), use_container_width=True)
with b: st.plotly_chart(line(trend, "Bill Month", "Total_Usage", "Total Portfolio Usage"), use_container_width=True)
