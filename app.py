from __future__ import annotations

import io
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

from aquaguard.data import generate_demo_data
from aquaguard.validation import validate_readings
from aquaguard.detector import detect_anomalies, group_events
from aquaguard.forecast import forecast_seven_days, forecast_mae
from aquaguard.simulator import simulate_savings
from aquaguard.evaluation import evaluate_detection

st.set_page_config(page_title="AquaGuard AI", page_icon="💧", layout="wide")

st.markdown("""
<style>
:root { --ag-bg:#07151b; --ag-panel:#10252d; --ag-line:#24434b; --ag-cyan:#36d6c3; }
.stApp { background:linear-gradient(145deg,#07151b 0%,#0a2028 60%,#0b1720 100%); }
.block-container { padding-top:1.5rem; max-width:1450px; }
h1,h2,h3 { color:#e8fbf8; }
[data-testid="stMetric"] { background:#10252d; border:1px solid #24434b; padding:14px; border-radius:14px; }
div[data-testid="stVerticalBlock"] > div:has(> div.stPlotlyChart) { border-radius:14px; }
.small-muted { color:#9db6bc; font-size:.9rem; }
.hero { padding:22px 26px; border:1px solid #24434b; border-radius:18px; background:linear-gradient(120deg,#102b33,#10212b); margin-bottom:18px; }
.hero p { color:#b7d1d3; margin-bottom:0; }
div.stButton > button[kind="primary"] { background:#17a995; border:0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>💧 AquaGuard AI</h1><p>Explainable water anomaly detection and demand planning for university campuses<br><b>Monitor → Detect → Explain → Prioritize → Simulate → Evaluate</b></p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.title("AquaGuard AI")
    st.caption("University water intelligence")
    page = st.radio("Workspace", ["Overview", "Anomaly review", "Demand forecast", "Scenario simulator", "Evaluation & data"])
    st.divider()
    st.caption("Prototype data")
    st.caption("5 virtual meters · 28 days · 15-minute intervals")
    st.caption("Synthetic benchmark — not field validation")

@st.cache_data
def demo_data():
    return generate_demo_data()

base = demo_data()
st.session_state.setdefault("readings", base.drop(columns=["is_injected_anomaly"]).copy())
st.session_state.setdefault("labels", base["is_injected_anomaly"].copy())
data = st.session_state.readings.copy()
labels = st.session_state.labels.copy()

if page == "Overview":
    clean, issues = validate_readings(data)
    detected = detect_anomalies(clean)
    events = group_events(detected)
    total_l = float(clean["volume_l"].sum())
    avg_day = total_l / max(clean["timestamp"].dt.date.nunique(), 1)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Readings", f"{len(clean):,}")
    c2.metric("Meters", clean["meter_id"].nunique())
    c3.metric("Total recorded use", f"{total_l:,.0f} L")
    c4.metric("Candidate events", len(events))
    st.subheader("Campus consumption")
    daily = clean.assign(date=clean.timestamp.dt.date).groupby("date",as_index=False).volume_l.sum()
    fig = px.line(daily, x="date", y="volume_l", markers=True, title="Daily campus water consumption")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Litres/day", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    left,right = st.columns([1.15,1])
    with left:
        st.subheader("Usage by meter")
        by_meter=clean.groupby("meter_id",as_index=False).volume_l.sum().sort_values("volume_l",ascending=False)
        f=px.bar(by_meter,x="meter_id",y="volume_l",color="meter_id",title="Total volume by meter")
        f.update_layout(template="plotly_dark",showlegend=False,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis_title="",yaxis_title="Litres")
        st.plotly_chart(f,use_container_width=True)
    with right:
        st.subheader("What AquaGuard does")
        st.markdown("""
        - **Monitor:** import interval meter readings.
        - **Detect:** compare each meter with its own recent baseline.
        - **Explain:** show expected use, excess volume and reason.
        - **Prioritize:** group persistent flags into candidate events.
        - **Plan:** forecast the next seven days.
        - **Simulate:** estimate the impact of faster response.
        """)
        st.info("An anomaly is a screening signal, not proof of a leak. Verify alerts with facilities staff.")
    if issues:
        st.warning("Data validation notes: " + "; ".join(issues))

elif page == "Anomaly review":
    st.subheader("Explainable anomaly review")
    st.write("A robust rolling baseline screens for unusually high readings. Consecutive flags are grouped to reduce alert noise.")
    clean, issues = validate_readings(data)
    result = detect_anomalies(clean)
    events = group_events(result)
    if result["is_anomaly"].any():
        st.metric("Flagged readings", f'{int(result.is_anomaly.sum()):,}')
        st.dataframe(result.loc[result.is_anomaly, ["meter_id","timestamp","volume_l","expected_l","excess_l","reason"]].sort_values("timestamp",ascending=False), use_container_width=True, hide_index=True)
    else:
        st.success("No candidate anomalies detected with the current settings.")
    st.subheader("Candidate events")
    if events:
        st.dataframe(pd.DataFrame(events), use_container_width=True, hide_index=True)
    else:
        st.caption("No grouped events to show.")
    with st.expander("Detection settings"):
        window = st.slider("Baseline window (readings)", 24, 192, 96, 8)
        sensitivity = st.slider("Sensitivity multiplier (k)", 2.0, 8.0, 4.0, 0.25)
        min_excess = st.number_input("Minimum excess (L / 15 min)", min_value=0.0, value=8.0, step=1.0)
        tuned = detect_anomalies(clean, window=window, k=sensitivity, min_excess=min_excess)
        st.caption(f"With these settings: {int(tuned.is_anomaly.sum())} readings flagged.")
    if issues: st.warning("; ".join(issues))

elif page == "Demand forecast":
    st.subheader("Seven-day water demand outlook")
    clean, issues = validate_readings(data)
    fc = forecast_seven_days(clean)
    hist = clean.assign(date=clean.timestamp.dt.date).groupby("date",as_index=False).volume_l.sum()
    hist["series"]="Observed"
    fc2=fc.rename(columns={"forecast_l":"volume_l"}).copy()
    fc2["series"]="Forecast"
    chart=pd.concat([hist[["date","volume_l","series"]],fc2[["date","volume_l","series"]]],ignore_index=True)
    fig=px.line(chart,x="date",y="volume_l",color="series",markers=True,title="Observed daily use and seven-day forecast")
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis_title="",yaxis_title="Litres/day")
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(fc.rename(columns={"date":"Forecast date","forecast_l":"Forecast (L/day)"}),use_container_width=True,hide_index=True)
    mae=forecast_mae(clean)
    st.metric("Rolling-origin holdout MAE", f"{mae:,.1f} L/day" if pd.notna(mae) else "Not enough history")
    st.caption("Forecast uses 70% same-weekday recent median + 30% recent 14-day median. Weather, occupancy and academic calendars are not modelled.")
    if issues: st.warning("; ".join(issues))

elif page == "Scenario simulator":
    st.subheader("Response-delay scenario simulator")
    st.write("Estimate water volume associated with a hypothetical constant abnormal flow.")
    a,b,c=st.columns(3)
    rate=a.number_input("Assumed leak / excess rate (L/hour)",min_value=0.0,value=25.0,step=1.0)
    current=b.number_input("Current response delay (hours)",min_value=1,value=48,step=1)
    target=c.number_input("Target response delay (hours)",min_value=0,value=8,step=1)
    result=simulate_savings(rate,current,target)
    x,y,z=st.columns(3)
    x.metric("Current scenario",f'{result["current_loss_l"]:,.0f} L')
    y.metric("Target scenario",f'{result["target_loss_l"]:,.0f} L')
    z.metric("Potential volume avoided",f'{result["avoided_l"]:,.0f} L')
    st.caption(f'Formula: leak rate × duration. Example: 25 L/hour × 48 hours = 1,200 L (1.2 m³).')
    st.info("This is a hypothetical estimate, not measured savings or confirmation that a leak exists.")

else:
    st.subheader("Evaluation and data management")
    st.write("Evaluation is meaningful only for the reproducible synthetic benchmark, which includes injected event labels.")
    clean, issues=validate_readings(data)
    result=detect_anomalies(clean)
    if labels is not None and len(labels)==len(result):
        y_true=labels.reset_index(drop=True).astype(bool)
        y_pred=result.is_anomaly.reset_index(drop=True).astype(bool)
        metrics=evaluate_detection(y_true,y_pred)
        cols=st.columns(6)
        for col,(name,val) in zip(cols,metrics.items()):
            col.metric(name, f"{val:.3f}" if isinstance(val,float) else f"{val:,}")
    else:
        st.warning("Ground-truth labels are unavailable for this uploaded dataset. Accuracy metrics are intentionally not invented.")
    st.divider()
    st.subheader("Upload meter readings")
    st.markdown("CSV columns required: `timestamp`, `meter_id`, `volume_l`. One row per meter per interval; volume must be non-negative litres.")
    uploaded=st.file_uploader("Choose CSV file",type=["csv"])
    if uploaded is not None:
        try:
            incoming=pd.read_csv(uploaded)
            valid, notes=validate_readings(incoming)
            st.success(f"Loaded {len(valid):,} valid readings from {valid.meter_id.nunique()} meters.")
            if notes: st.warning("; ".join(notes))
            if st.button("Use uploaded dataset",type="primary"):
                st.session_state.readings=valid
                st.session_state.labels=None
                st.rerun()
        except Exception as exc:
            st.error(f"Could not read this CSV: {exc}")
    st.download_button("Download current readings CSV",data=data.to_csv(index=False).encode("utf-8"),file_name="aquaguard_readings.csv",mime="text/csv")
    if issues: st.warning("; ".join(issues))

st.divider()
st.caption("AquaGuard AI · Student prototype · Synthetic data unless otherwise stated · Prepared by Farid Ahmad Khan")
