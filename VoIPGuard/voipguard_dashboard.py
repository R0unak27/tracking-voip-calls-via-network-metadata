# voip_guard_app.py
import streamlit as st
import pandas as pd
import winsound

# -------------------------------
# Function to detect alerts
# -------------------------------
def detect_alerts(df, high_freq_threshold=100):
    blacklisted_calls = df[df['is_blacklisted'] == True]
    suspicious_calls = df[
        (df['call_quality'] < 2.5) |
        (df['call_status'].isin(['failed', 'dropped'])) |
        (df['number_of_previous_calls'] > high_freq_threshold)
    ]
    alerts = pd.concat([blacklisted_calls, suspicious_calls]).drop_duplicates()
    return alerts

# -------------------------------
# Function to play alert sound
# -------------------------------
def play_alert():
    winsound.Beep(1000, 500)  # 1000 Hz for 0.5 seconds

# -------------------------------
# Streamlit App Layout
# -------------------------------
st.title("📞 VoIP Guard - Call Monitoring System")
st.write("Upload your CDR CSV file to detect blacklisted and suspicious calls.")

# Upload CSV
uploaded_file = st.file_uploader("Upload CDR CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("CSV loaded successfully!")

    # Show basic stats
    st.subheader("Summary Statistics")
    st.write(f"Total calls: {len(df)}")
    st.write(f"Total blacklisted calls: {df[df['is_blacklisted']==True].shape[0]}")
    st.write(f"Suspicious calls detected: {len(detect_alerts(df))}")

    # Show first 5 rows
    st.subheader("Sample Data")
    st.dataframe(df.head())

    # Detect alerts
    alerts = detect_alerts(df)
    
    # Limit alerts to max 10 for demo
    st.subheader("🚨 Alerts (Max 10 shown)")
    for index, call in alerts.head(10).iterrows():
        st.warning(f"Blacklisted/Suspicious Call!\nCaller ID: {call['caller_id']}\nCallee ID: {call['callee_id']}")
        play_alert()

    # Option to download alerts CSV
    st.download_button(
        label="Download Alerts CSV",
        data=alerts.to_csv(index=False),
        file_name="VoIP_alerts.csv",
        mime="text/csv"
    )

    # Call type distribution chart
    st.subheader("Call Type Distribution")
    st.bar_chart(df['call_type'].value_counts())

    # Top 10 blacklisted callers
    st.subheader("Top 10 Blacklisted Callers")
    top_callers = df[df['is_blacklisted']==True]['caller_id'].value_counts().head(10)
    st.bar_chart(top_callers)

