from __future__ import annotations
import streamlit as st
from utils.ui import apply_css, metric_card
from utils.calculations import monthly_summary, money_fmt, num_fmt
from utils.alerts import build_alerts, generate_insight
from utils.charts import line

st.set_page_config(page_title="Property Scorecard", page_icon="🏥", layout="wide")
apply_css()
st.title("3. Property Scorecard")
df = st.session_state.get("raw_df")
if df is None: st.warning("Open the main app first so data can load."); st.stop()
monthly = monthly_summary(df); alerts = build_alerts(monthly)
props = sorted(df["Property Name"].dropna().unique())
prop = st.selectbox("Select Property", props)
prop_df = monthly[monthly["Property Name"] == prop]
utils = ["All Utilities"] + sorted(prop_df["Utility"].dropna().unique().tolist())
utility = st.selectbox("Utility", utils)
if utility != "All Utilities": prop_df = prop_df[prop_df["Utility"] == utility]
latest = prop_df.sort_values("Bill Month").tail(1)
row = latest.iloc[0] if not latest.empty else None
city_state = df[df["Property Name"]==prop][["City","State"]].drop_duplicates().head(1)
st.caption(" • ".join(city_state.iloc[0].astype(str).tolist()) if not city_state.empty else "")

if row is not None:
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: metric_card("Current Month Cost", money_fmt(row["Total_Cost"]))
    with c2: metric_card("Current Usage", num_fmt(row["Total_Usage"]))
    with c3: metric_card("# Treatments", num_fmt(row["Treatments"]))
    with c4: metric_card("Cost / Treatment", f"${row['Cost_per_Treatment']:,.2f}" if row['Cost_per_Treatment']==row['Cost_per_Treatment'] else "—")
    with c5: metric_card("Usage / Treatment", num_fmt(row["Usage_per_Treatment"]))
    with c6: metric_card("Days Billed", num_fmt(row["Days_Billed"]))

st.subheader("Trends")
a,b,c = st.columns(3)
trend = prop_df.groupby("Bill Month", as_index=False).agg(Total_Cost=("Total_Cost","sum"), Total_Usage=("Total_Usage","sum"), Treatments=("Treatments","sum"))
with a: st.plotly_chart(line(trend,"Bill Month","Total_Cost","Cost Trend"), use_container_width=True)
with b: st.plotly_chart(line(trend,"Bill Month","Total_Usage","Usage Trend"), use_container_width=True)
with c: st.plotly_chart(line(trend,"Bill Month","Treatments","Treatments Trend"), use_container_width=True)

left,right = st.columns([2,1])
with left:
    st.subheader("Utility Summary")
    latest_month = prop_df["Bill Month"].max()
    summary = prop_df[prop_df["Bill Month"]==latest_month]
    st.dataframe(summary[["Utility","Provider","Days_Billed","Total_Usage","Total_Usage_Change","Total_Cost","Total_Cost_Change","Cost_per_Treatment"]], use_container_width=True, hide_index=True)
    st.subheader("Billing History")
    raw = df[df["Property Name"]==prop].sort_values("Billing Date", ascending=False)
    st.dataframe(raw[["Billing Date","Utility","Provider","Number Days Billed","Usage","$ Amount","# Treatments","Cost per Treatment"]], use_container_width=True, hide_index=True)
with right:
    st.subheader("AI Insight")
    prop_alerts = alerts[(alerts["Property Name"]==prop)].sort_values("Estimated Monthly Impact", ascending=False)
    if not prop_alerts.empty:
        st.warning(generate_insight(prop_alerts.iloc[0]))
        st.caption(f"Alert: {prop_alerts.iloc[0]['Alert Level']} • {prop_alerts.iloc[0]['Alert Type']}")
    st.subheader("Analyst Notes")
    note = st.text_area("Add note", placeholder="Example: Facility confirmed water leak was repaired on 6/10.")
    if st.button("Save Note"):
        st.success("Note saved for this session. Add database storage in V2 to persist notes for all users.")
    st.subheader("Facility Ranking")
    latest_all = monthly[monthly["Bill Month"]==monthly["Bill Month"].max()].groupby("Property Name", as_index=False).agg(Cost_per_Treatment=("Cost_per_Treatment","mean"), Usage_per_Treatment=("Usage_per_Treatment","mean"))
    rank = latest_all[latest_all["Property Name"]==prop]
    if not rank.empty:
        cpt_rank = latest_all["Cost_per_Treatment"].rank(ascending=False, method="min")[latest_all["Property Name"]==prop].iloc[0]
        st.info(f"Cost/Treatment Rank: #{int(cpt_rank)} of {len(latest_all)}")
