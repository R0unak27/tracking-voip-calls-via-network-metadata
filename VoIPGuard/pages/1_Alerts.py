import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:5000/api/calls"

st.set_page_config(page_title="Alerts", layout="wide")
st.title("⚠️ Suspicious Call Alerts")

# Fetch Data
response = requests.get(API_URL)
data = response.json().get("items", []) if response.status_code == 200 else []

if data:
    df = pd.DataFrame(data)
    df_alerts = df[df["suspicious"] == True]

    if not df_alerts.empty:
        # --- Summary Section ---
        st.markdown("### 📊 Alert Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Alerts", len(df_alerts))
        c2.metric("High Risk", df_alerts[df_alerts["risk_score"] >= 70].shape[0])
        c3.metric("Blacklisted Callers", df_alerts[df_alerts["is_blacklisted"] == True].shape[0])

        st.markdown("---")
        st.markdown("### 🚨 Active Alerts")

        # --- Alert Cards ---
        for _, row in df_alerts.iterrows():
            with st.container():
                risk = row["risk_score"]

                # Risk Badge Color
                if risk >= 70:
                    badge_color = "red"
                    badge_text = "🔴 HIGH RISK"
                elif risk >= 40:
                    badge_color = "orange"
                    badge_text = "🟠 MEDIUM RISK"
                else:
                    badge_color = "green"
                    badge_text = "🟢 LOW RISK"

                st.markdown(f"""
                <div style="
                    border:1px solid #ddd;
                    border-left: 6px solid {badge_color};
                    border-radius:10px;
                    padding:15px;
                    margin-bottom:15px;
                    background-color:#f9f9f9">
                    
                    <h4 style="margin:0;">📞 {row['caller_id']} → {row['callee_id']}</h4>
                    <p style="margin:5px 0;">
                        <b>Protocol:</b> {row['protocol']} &nbsp;|&nbsp;
                        <b>Status:</b> {row['call_status']} &nbsp;|&nbsp;
                        <b>Duration:</b> {row['call_duration_seconds']} sec
                    </p>
                    <p style="margin:5px 0;">
                        <b>Source:</b> {row['source_ip']} ({row['caller_location']}) <br>
                        <b>Destination:</b> {row['destination_ip']} ({row['callee_location']})
                    </p>
                    <p style="margin:5px 0;color:{badge_color};"><b>{badge_text}</b> | Risk Score: {risk}</p>
                    <details>
                        <summary style="cursor:pointer;">🔎 Suspicion Reasons</summary>
                        <ul>
                            {''.join(f"<li>{reason}</li>" for reason in row['suspicion_reasons'])}
                        </ul>
                    </details>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("✅ No suspicious calls detected.")
else:
    st.error("⚠️ Backend not reachable. Please check API.")
