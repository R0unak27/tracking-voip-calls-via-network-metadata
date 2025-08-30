import streamlit as st
import pandas as pd

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="VoIPGuard",
    layout="wide"
)

# ----------------------------
# SIDEBAR NAVIGATION
# ----------------------------
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to", ["Home", "Upload Data", "Alerts Dashboard"])

# ----------------------------
# HOME PAGE
# ----------------------------
if page == "Home":
    st.title("📞 VoIPGuard – Real-time VoIP Monitoring")
    st.markdown("""
    Welcome to **VoIPGuard**!  

    🚀 Upload VoIP packet data to detect anomalies and generate alerts.  
    Use the **Upload Data** section to start.
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=200)

# ----------------------------
# UPLOAD DATA PAGE
# ----------------------------
elif page == "Upload Data":
    st.title("📂 Upload Packet Data (CSV)")

    uploaded_file = st.file_uploader("Upload VoIP Packet CSV", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state["packet_data"] = df  # save for dashboard page
        st.success("✅ File uploaded successfully!")
        st.subheader("📊 Preview of Uploaded Data")
        st.dataframe(df.head())

# ----------------------------
# ALERTS / DASHBOARD PAGE
# ----------------------------
elif page == "Alerts Dashboard":
    st.title("🚨 VoIP Alerts Dashboard")

    # Check if packet data exists
    if "packet_data" not in st.session_state:
        st.warning("⚠️ Please upload packet data first in the 'Upload Data' section.")
    else:
        df = st.session_state["packet_data"]

        # ---------------- DUMMY ALERT LOGIC ----------------
        alerts = []
        for i, row in df.iterrows():
            if "SIP" in str(row.get("Protocol", "")):
                alerts.append({"Packet": i, "Issue": "Suspicious SIP packet"})
            if row.get("Length", 0) > 500:
                alerts.append({"Packet": i, "Issue": "Unusually large packet"})

        # ---------------- METRICS / KPIs ----------------
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Packets", len(df))
        col2.metric("Suspicious Packets", len(alerts))
        col3.metric("Alert Rate", f"{(len(alerts)/len(df))*100:.2f}%" if len(df)>0 else "0%")

        # ---------------- ALERTS TABLE ----------------
        if alerts:
            st.error("⚠️ Threats Detected!")
            alerts_df = pd.DataFrame(alerts)
            st.table(alerts_df)
        else:
            st.success("✅ No anomalies detected. Traffic looks clean.")

        # ---------------- VISUALIZATIONS ----------------
        st.write("### 📊 Protocol Distribution")
        st.bar_chart(df["Protocol"].value_counts())

        st.write("### 📈 Packet Size Trend")
        st.line_chart(df["Length"])
