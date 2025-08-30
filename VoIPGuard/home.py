import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "http://localhost:5000/api/calls"

st.set_page_config(page_title="VoIP Dashboard", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📋 Call Records", "🚨 Alerts"])

# Fetch Data
response = requests.get(API_URL)
data = response.json().get("items", []) if response.status_code == 200 else []
df = pd.DataFrame(data) if data else pd.DataFrame()

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

        # Highlight suspicious rows red + bold
        def highlight_row(row):
            if row["suspicious"]:
                return ["background-color: #ffcccc; font-weight: bold;" for _ in row]
            else:
                return ["" for _ in row]

        st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)
    else:
        st.warning("⚠️ No call records found")

# ============ ALERTS ============
# ============ ALERTS ============
elif page == "🚨 Alerts":
    st.title("🚨 Suspicious Calls & Alerts")

    if not df.empty:
        alerts = df[df["suspicious"] == True]

        # Show quick stats
        st.subheader("📊 Alert Summary")
        col1, col2 = st.columns(2)
        col1.metric("Total Suspicious Calls", len(alerts))
        col2.metric("High Risk (Score ≥ 70)", alerts[alerts["risk_score"] >= 70].shape[0])

        if not alerts.empty:
            # Convert call_time to datetime
            if "call_time" in alerts.columns:
                alerts["call_time"] = pd.to_datetime(alerts["call_time"], errors="coerce")

            # Timeline chart (Suspicious calls by time)
            if "call_time" in alerts.columns:
                st.subheader("📈 Suspicious Calls Over Time")
                time_counts = alerts.groupby(alerts["call_time"].dt.floor("min")).size()
                st.line_chart(time_counts)

            # Risk score distribution
         # Risk score distribution
            st.subheader("⚠️ Risk Score Distribution (Suspicious Only)")

            fig, ax = plt.subplots(figsize=(5,2))  # 👈 very compact
            ax.hist(alerts["risk_score"], bins=10, color="#FF6B6B", edgecolor="black")
            ax.set_xlabel("Risk Score")
            ax.set_ylabel("Calls")
            
            st.pyplot(fig, use_container_width=False)  # 👈 ab stretch nahi karega




            # Detailed suspicious calls table
            st.subheader("📋 Detailed Suspicious Calls")
            st.dataframe(alerts, use_container_width=True)
        else:
            st.success("✅ No suspicious calls detected")

    else:
        st.warning("⚠️ No call records found")
