from __future__ import annotations
import streamlit as st
from utils.ui import apply_css, metric_card
from utils.calculations import monthly_summary, filter_df
from utils.alerts import build_alerts

st.set_page_config(page_title="Exception Center", page_icon="⚠️", layout="wide")
apply_css()
st.title("2. Exception Center")
st.caption("Focus on what needs your attention")
df = st.session_state.get("raw_df")
if df is None: st.warning("Open the main app first so data can load."); st.stop()
monthly = monthly_summary(df); alerts = build_alerts(monthly)

states = ["All"] + sorted(df["State"].dropna().unique().tolist())
props = ["All"] + sorted(df["Property Name"].dropna().unique().tolist())
utils = ["All"] + sorted(df["Utility"].dropna().unique().tolist())
levels = ["All", "Critical", "Review", "Info", "Normal"]
months = sorted(monthly["Bill Month"].dropna().unique())

c1,c2,c3,c4,c5 = st.columns(5)
state = c1.multiselect("State", states, default=["All"])
prop = c2.multiselect("Property", props, default=["All"])
utility = c3.multiselect("Utility", utils, default=["All"])
level = c4.selectbox("Alert Level", levels)
date = c5.selectbox("Month", months, index=len(months)-1 if months else 0, format_func=lambda x: x.strftime('%b %Y') if hasattr(x,'strftime') else str(x))

view = filter_df(alerts, state, prop, utility, [date, date])
if level != "All": view = view[view["Alert Level"] == level]

c1,c2,c3,c4 = st.columns(4)
with c1: metric_card("Critical Alerts", str((view["Alert Level"]=="Critical").sum()))
with c2: metric_card("Review Alerts", str((view["Alert Level"]=="Review").sum()))
with c3: metric_card("Info Alerts", str((view["Alert Level"]=="Info").sum()))
with c4: metric_card("Normal/Resolved", str((view["Alert Level"]=="Normal").sum()))

st.subheader("All Exceptions")
cols = ["Alert Level","Property Name","State","Utility","Alert Type","Reason","Total_Usage_Change","Total_Cost_Change","Cost_per_Treatment_Change","Days_Billed","Last_Bill_Date","Estimated Monthly Impact"]
st.dataframe(view.sort_values(["Alert Level","Estimated Monthly Impact"], ascending=[True, False])[[c for c in cols if c in view.columns]], use_container_width=True, hide_index=True)
st.download_button("Export exceptions as CSV", view.to_csv(index=False).encode(), "exceptions.csv", "text/csv")
