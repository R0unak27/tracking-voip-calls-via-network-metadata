import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:5000/api/calls"

st.set_page_config(page_title="VoIP Dashboard", layout="wide")

st.title("📞 VoIP Call Tracing Dashboard")
st.markdown("### Tracing VoIP calls via network metadata")

# Fetch data
response = requests.get(API_URL)
data = response.json().get("items", []) if response.status_code == 200 else []

if data:
    df = pd.DataFrame(data)

    total_calls = len(df)
    suspicious_calls = df[df["suspicious"] == True].shape[0]
    avg_duration = round(df["call_duration_seconds"].mean(), 2)
    high_risk = df[df["risk_score"] >= 70].shape[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Calls", total_calls)
    col2.metric("Suspicious Calls", suspicious_calls)
    col3.metric("Avg Duration (s)", avg_duration)
    col4.metric("High Risk Calls", high_risk)

    st.bar_chart(df["risk_score"])

else:
    st.warning("⚠️ No call records found")
