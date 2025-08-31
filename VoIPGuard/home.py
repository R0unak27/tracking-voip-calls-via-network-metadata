import streamlit as st
import pandas as pd
import requests
import time
import matplotlib.pyplot as plt

API_URL = "http://localhost:5000/api/calls"
MODAL_DURATION = 5  # seconds

st.set_page_config(page_title="VoIP Dashboard", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "🏠 Home"
page = st.sidebar.radio("Go to", ["🏠 Home", "📋 Call Records", "🚨 Alerts"],
                        index=["🏠 Home", "📋 Call Records", "🚨 Alerts"].index(st.session_state["current_page"]))

# Fetch data
response = requests.get(API_URL)
data = response.json().get("items", []) if response.status_code == 200 else []
df = pd.DataFrame(data) if data else pd.DataFrame()

# Track modal state
if "modal_open" not in st.session_state:
    st.session_state["modal_open"] = False
if "modal_time" not in st.session_state:
    st.session_state["modal_time"] = 0
if "last_alert_id" not in st.session_state:
    st.session_state["last_alert_id"] = None

# System-wide alerts
alerts = df[df["suspicious"] == True] if not df.empty and "suspicious" in df.columns else pd.DataFrame()
latest_alert = alerts.iloc[0] if not alerts.empty else None
latest_alert_id = str(latest_alert["_id"]) if latest_alert is not None and "_id" in latest_alert else None

# Trigger modal if new suspicious call
if latest_alert_id and latest_alert_id != st.session_state["last_alert_id"]:
    st.session_state["modal_open"] = True
    st.session_state["modal_time"] = time.time()
    st.session_state["last_alert_id"] = latest_alert_id

    # 🔊 Play sound without showing audio bar
    st.markdown(
        """
        <style>
        audio { display:none; }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.audio("https://www.soundjay.com/buttons/sounds/beep-07.mp3", start_time=0)

# Display modal if open (NO BUTTON, auto-dismiss after MODAL_DURATION)
if st.session_state["modal_open"] and latest_alert is not None:
    st.markdown(
        f"""
        <style>
        .modal-backdrop {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0,0,0,0.6); z-index: 9999;
        }}
        .modal-window {{
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: #fff; border-radius: 20px; box-shadow: 0 0 50px #2228;
            min-width: 360px; max-width: 90vw; padding: 2em; z-index: 10000;
            text-align: center; animation: fadeIn 0.5s;
        }}
        .modal-title {{
            font-size: 2em; font-weight: bold; margin-bottom: 0.3em;
        }}
        .modal-icon {{
            font-size: 2.5em; vertical-align: middle; margin-right: 0.4em;
            animation: blink 1s infinite;
        }}
        @keyframes blink {{
            0%, 50%, 100% {{ opacity: 1; }}
            25%, 75% {{ opacity: 0; }}
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translate(-50%, -55%); }}
            to {{ opacity: 1; transform: translate(-50%, -50%); }}
        }}
        </style>
        <div class="modal-backdrop"></div>
        <div class="modal-window">
            <span class="modal-icon">⚠️</span>
            <span class="modal-title">Critical Alert!</span>
            <div style="margin-top: 0.5em; font-size: 1.15em;">
                Suspicious call detected!<br>
                <b>Caller:</b> {latest_alert['caller_id']}<br>
                <b>Callee:</b> {latest_alert['callee_id']}<br>
                <b>Risk Score:</b> <span style='color:#b20000;font-weight:bold;'>{latest_alert['risk_score']}</span><br>
                <b>Source IP:</b> {latest_alert.get('source_ip', 'N/A')}<br>
                <b>Destination IP:</b> {latest_alert.get('destination_ip', 'N/A')}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Auto-dismiss after timeout (NOW 5 seconds)
    if time.time() - st.session_state["modal_time"] > MODAL_DURATION:
        st.session_state["modal_open"] = False

# ============ HOME PAGE ============
if page == "🏠 Home":
    st.title("📞 VoIP Call Tracing Dashboard")
    st.markdown("Monitor and trace suspicious VoIP calls using network metadata")

    if not df.empty:
        # Metrics
        total_calls = len(df)
        suspicious_calls = df[df["suspicious"] == True].shape[0]
        avg_duration = round(df["call_duration_seconds"].mean(), 2)
        high_risk = df[df["risk_score"] >= 70].shape[0]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Calls", total_calls)
        col2.metric("Suspicious Calls", suspicious_calls)
        col3.metric("Avg Duration (s)", avg_duration)
        col4.metric("High Risk Calls", high_risk)

        # Risk score distribution
        st.subheader("📊 Risk Score Distribution")
        st.bar_chart(df["risk_score"])

        # Suspicious vs Normal Pie Chart
        st.subheader("🚨 Suspicious vs Normal Calls")
        fig, ax = plt.subplots()
        suspicious_count = df["suspicious"].sum()
        normal_count = len(df) - suspicious_count
        ax.pie([suspicious_count, normal_count],
               labels=["Suspicious", "Normal"],
               autopct="%1.1f%%",
               startangle=90,
               colors=["#FF6B6B", "#4ECDC4"])
        ax.axis("equal")
        st.pyplot(fig)

    else:
        st.warning("⚠️ No call records found")

# ============ CALL RECORDS ============
elif page == "📋 Call Records":
    st.title("📋 All Call Records")
    if not df.empty:
        caller_filter = st.text_input("🔍 Search by Caller ID")
        if caller_filter:
            df = df[df["caller_id"].str.contains(caller_filter, case=False)]

        # Highlight suspicious rows
        def highlight_row(row):
            if row["suspicious"]:
                return ["background-color: #ffcccc; font-weight: bold;" for _ in row]
            else:
                return ["" for _ in row]

        st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)
    else:
        st.warning("⚠️ No call records found")

# ============ ALERTS ============
elif page == "🚨 Alerts":
    st.title("🚨 Suspicious Calls & Alerts")

    if not df.empty:
        alerts = df[df["suspicious"] == True]

        st.subheader("📊 Alert Summary")
        col1, col2 = st.columns(2)
        col1.metric("Total Suspicious Calls", len(alerts))
        col2.metric("High Risk (Score ≥ 70)", alerts[alerts["risk_score"] >= 70].shape[0])

        if not alerts.empty:
            if "call_time" in alerts.columns:
                alerts["call_time"] = pd.to_datetime(alerts["call_time"], errors="coerce")

            if "call_time" in alerts.columns:
                st.subheader("📈 Suspicious Calls Over Time")
                time_counts = alerts.groupby(alerts["call_time"].dt.floor("min")).size()
                st.line_chart(time_counts)

            st.subheader("📋 Detailed Suspicious Calls")

            # No highlight, no scroll, just show table
            st.dataframe(alerts, use_container_width=True)

        else:
            st.success("✅ No suspicious calls detected")
    else:
        st.warning("⚠️ No call records found")