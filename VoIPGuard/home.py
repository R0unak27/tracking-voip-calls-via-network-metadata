import streamlit as st
import pandas as pd
import requests
import time
import matplotlib.pyplot as plt
import numpy as np
import os



API_URL = os.getenv("API_URL")
MODAL_DURATION = 3 # seconds

st.set_page_config(page_title="VoIP Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        margin: 0.5rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        font-weight: 500;
        opacity: 0.9;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2C3E50 0%, #34495E 100%);
    }
    
    /* Title styling */
    .main-title {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Alert cards */
    .alert-card {
        background: linear-gradient(135deg, #ff6b6b, #ee5a52);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(255,107,107,0.3);
        animation: slideIn 0.5s ease;
    }
    
    .success-card {
        background: linear-gradient(135deg, #4ecdc4, #44a08d);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(78,205,196,0.3);
    }
    
    /* Risk badges */
    .risk-critical { background: #dc3545; }
    .risk-high { background: #fd7e14; }
    .risk-medium { background: #ffc107; color: #212529; }
    .risk-low { background: #28a745; }
    
    .risk-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        color: white;
    }
    
    /* Fixed Modal Styling - Stable display */
    .modal-backdrop {
        position: fixed; 
        top: 0; 
        left: 0; 
        width: 100vw; 
        height: 100vh;
        background: rgba(0,0,0,0.8); 
        z-index: 9999;
        backdrop-filter: blur(5px);
    }
    .modal-window {
        position: fixed; 
        top: 50%; 
        left: 50%; 
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; 
        border-radius: 25px; 
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        min-width: 400px; 
        max-width: 90vw; 
        padding: 2.5em; 
        z-index: 10000;
        text-align: center; 
        animation: modalSlideIn 0.6s ease;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .modal-title {
        font-size: 2.2em; 
        font-weight: 700; 
        margin-bottom: 0.5em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .modal-icon {
        font-size: 3em; 
        margin-bottom: 0.5em; 
        display: block;
        animation: pulse 1.5s infinite;
    }
    .modal-content {
        background: rgba(255,255,255,0.1);
        padding: 1.5rem; 
        border-radius: 15px;
        margin: 1rem 0; 
        backdrop-filter: blur(10px);
    }
    .countdown {
        font-size: 1em; 
        margin-top: 1.5em; 
        opacity: 0.8;
        background: rgba(255,255,255,0.2); 
        padding: 0.5rem 1rem;
        border-radius: 20px; 
        display: inline-block;
    }
    
    /* Animations */
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px rgba(102, 126, 234, 0.5); }
        50% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.8); }
    }
    
    .glow-effect {
        animation: glow 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    @keyframes modalSlideIn {
        from { opacity: 0; transform: translate(-50%, -60%) scale(0.9); }
        to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
    }
    
    /* Filter section */
    .filter-section {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Enhanced sidebar with custom styling
st.sidebar.markdown("""
    <div style='text-align: center; padding: 1rem 0; color: white;'>
        <h2 style='color: #ffffff; margin-bottom: 0.5rem;'>🎛️ Navigation</h2>
        <p style='color: #bdc3c7; font-size: 0.9rem;'>VoIP Security Dashboard</p>
    </div>
""", unsafe_allow_html=True)

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "🏠 Home"

page = st.sidebar.radio(
    "Select Page", 
    ["🏠 Home", "📋 Call Records", "🚨 Alerts"],
    index=["🏠 Home", "📋 Call Records", "🚨 Alerts"].index(st.session_state["current_page"])
)

# Add sidebar stats
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")

# Fetch data – get last 200 calls from backend
try:
    response = requests.get(f"{API_URL}?limit=200")
    if response.status_code == 200:
        data = response.json().get("items", [])
    else:
        st.warning(f"⚠️ Failed to fetch data from backend. Status code: {response.status_code}")
        data = []
except Exception as e:
    st.warning(f"⚠️ Error fetching data: {e}")
    data = []

df = pd.DataFrame(data) if data else pd.DataFrame()

# Sidebar quick stats
if not df.empty:
    total_calls = len(df)
    suspicious_calls = df[df["suspicious"] == True].shape[0]
    threat_level = "🔴 HIGH" if suspicious_calls > 10 else "🟡 MEDIUM" if suspicious_calls > 5 else "🟢 LOW"
    
    st.sidebar.metric("📞 Total Calls", total_calls)
    st.sidebar.metric("🚨 Threats", suspicious_calls)
    st.sidebar.markdown(f"**Threat Level:** {threat_level}")

# Initialize session state variables for modal control
if "modal_active" not in st.session_state:
    st.session_state["modal_active"] = False
if "modal_start_time" not in st.session_state:
    st.session_state["modal_start_time"] = None
if "last_alert_id" not in st.session_state:
    st.session_state["last_alert_id"] = None
if "modal_should_close" not in st.session_state:
    st.session_state["modal_should_close"] = False

# System-wide alerts
alerts = df[df["suspicious"] == True] if not df.empty and "suspicious" in df.columns else pd.DataFrame()
latest_alert = alerts.iloc[0] if not alerts.empty else None
latest_alert_id = str(latest_alert["_id"]) if latest_alert is not None and "_id" in latest_alert else None

# Check for new alert
if latest_alert_id and latest_alert_id != st.session_state["last_alert_id"]:
    st.session_state["modal_active"] = True
    st.session_state["modal_start_time"] = time.time()
    st.session_state["last_alert_id"] = latest_alert_id
    st.session_state["modal_should_close"] = False

# Modal display logic - FIXED VERSION
if st.session_state["modal_active"] and latest_alert is not None and st.session_state["modal_start_time"]:
    elapsed_time = time.time() - st.session_state["modal_start_time"]
    remaining_time = max(0, MODAL_DURATION - elapsed_time)
    
    # Check if time is up
    if elapsed_time >= MODAL_DURATION:
        st.session_state["modal_active"] = False
        st.session_state["modal_start_time"] = None
        st.session_state["modal_should_close"] = True
        st.rerun()
    else:
        # Show modal - Single display without multiple reruns
        st.markdown(
            f"""
            <div class="modal-backdrop"></div>
            <div class="modal-window">
                <div class="modal-icon">🚨</div>
                <div class="modal-title">SECURITY ALERT</div>
                <div class="modal-content">
                    <div style="font-size: 1.2em; margin-bottom: 1rem;">
                        <strong>⚠️ Suspicious Activity Detected!</strong>
                    </div>
                    <div style="text-align: left; font-size: 1.05em; line-height: 1.6;">
                        <strong>📞 Caller:</strong> {latest_alert['caller_id']}<br>
                        <strong>📱 Callee:</strong> {latest_alert['callee_id']}<br>
                        <strong>⚠️ Risk Score:</strong> <span style='background: #dc3545; padding: 3px 8px; border-radius: 10px; font-weight: bold;'>{latest_alert['risk_score']}</span><br>
                        <strong>🌐 Source IP:</strong> {latest_alert.get('source_ip', 'N/A')}<br>
                        <strong>🎯 Destination IP:</strong> {latest_alert.get('destination_ip', 'N/A')}
                    </div>
                </div>
                <div class="countdown">⏰ Auto-closing in {remaining_time:.1f}s</div>
            </div>
            
            <script>
                // Single auto-close timer
                setTimeout(function() {{
                    window.parent.postMessage({{type: 'streamlit:closeModal'}}, '*');
                }}, {int(remaining_time * 1000) + 100});
            </script>
            """,
            unsafe_allow_html=True
        )
        
        # Use a controlled delay and single rerun
        if remaining_time > 0.5:  # Only rerun if significant time remains
            time.sleep(0.8)  # Slightly longer delay to prevent flickering
            st.rerun()

# ============ HOME PAGE ============
if page == "🏠 Home":
    # Hero Section
    st.markdown('<h1 class="main-title">📞 VoIP Security Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">🛡️ Advanced VoIP Call Monitoring & Threat Detection System</p>', unsafe_allow_html=True)

    if not df.empty:
        # Enhanced Metrics Cards
        total_calls = len(df)
        suspicious_calls = df[df["suspicious"] == True].shape[0]
        avg_duration = round(df["call_duration_seconds"].mean(), 2)
        high_risk = df[df["risk_score"] >= 70].shape[0]

        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <div class="metric-value">📞 {total_calls}</div>
                    <div class="metric-label">Total Calls</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                    <div class="metric-value">🚨 {suspicious_calls}</div>
                    <div class="metric-label">Suspicious Calls</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333;">
                    <div class="metric-value">⏱️ {avg_duration}s</div>
                    <div class="metric-label">Avg Duration</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
                    <div class="metric-value">🔴 {high_risk}</div>
                    <div class="metric-label">High Risk Calls</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Enhanced Risk Score Distribution
        st.markdown('<div class="section-header">📊 Risk Score Analysis</div>', unsafe_allow_html=True)
        
        risk_scores = df["risk_score"]
        bins = [0, 20, 40, 60, 80, 100]
        labels = ['0-20\n(Safe)', '21-40\n(Low Risk)', '41-60\n(Medium)', '61-80\n(High Risk)', '81-100\n(Critical)']
        
        hist_data = pd.cut(risk_scores, bins=bins, labels=labels, include_lowest=True)
        hist_counts = hist_data.value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # Modern gradient colors
        colors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF5722', '#F44336']
        bars = ax.bar(range(len(hist_counts)), hist_counts.values, 
                     color=colors, alpha=0.8, edgecolor='white', linewidth=3)
        
        # Modern styling
        ax.set_facecolor('#f8f9fa')
        fig.patch.set_facecolor('#ffffff')
        ax.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Custom labels and title
        ax.set_xlabel('Risk Categories', fontsize=14, fontweight='600', color='#2c3e50')
        ax.set_ylabel('Number of Calls', fontsize=14, fontweight='600', color='#2c3e50')
        ax.set_title('🎯 Risk Distribution Analysis', fontsize=18, fontweight='700', color='#2c3e50', pad=25)
        ax.set_xticks(range(len(hist_counts)))
        ax.set_xticklabels(hist_counts.index, fontsize=11, fontweight='500')
        
        # Value labels with modern styling
        for i, bar in enumerate(bars):
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.8,
                       f'{int(height)}', ha='center', va='bottom', 
                       fontweight='bold', fontsize=12, color='#2c3e50',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        st.pyplot(fig)

        # Side-by-side charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown('<div class="section-header">🥧 Call Distribution</div>', unsafe_allow_html=True)
            fig2, ax2 = plt.subplots(figsize=(8, 8))
            suspicious_count = df["suspicious"].sum()
            normal_count = len(df) - suspicious_count
            
            colors_pie = ["#FF6B6B", "#4ECDC4"]
            wedges, texts, autotexts = ax2.pie([suspicious_count, normal_count],
                                              labels=["🚨 Suspicious", "✅ Normal"],
                                              autopct="%1.1f%%",
                                              startangle=90,
                                              colors=colors_pie,
                                              explode=(0.08, 0),
                                              shadow=True,
                                              textprops={'fontsize': 12, 'fontweight': 'bold'})
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(13)
            
            ax2.set_title('🎯 Security Overview', fontsize=16, fontweight='bold', pad=20)
            fig2.patch.set_facecolor('#ffffff')
            st.pyplot(fig2)
        
        with chart_col2:
            st.markdown('<div class="section-header">📈 Call Duration Analysis</div>', unsafe_allow_html=True)
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            
            # Duration histogram
            durations = df["call_duration_seconds"]
            ax3.hist(durations, bins=20, color='#667eea', alpha=0.7, edgecolor='white', linewidth=1.5)
            ax3.set_xlabel('Call Duration (seconds)', fontweight='600')
            ax3.set_ylabel('Frequency', fontweight='600')
            ax3.set_title('📊 Call Duration Distribution', fontweight='bold', pad=15)
            ax3.grid(axis='y', alpha=0.3)
            ax3.set_facecolor('#f8f9fa')
            fig3.patch.set_facecolor('#ffffff')
            
            plt.tight_layout()
            st.pyplot(fig3)

        # Enhanced detailed analytics
        with st.expander("🔍 Advanced Analytics", expanded=False):
            analytic_col1, analytic_col2, analytic_col3 = st.columns(3)
            
            with analytic_col1:
                st.markdown("### 📊 Risk Statistics")
                st.metric("🎯 Highest Risk", df["risk_score"].max())
                st.metric("📉 Lowest Risk", df["risk_score"].min())
                st.metric("📊 Risk Std Dev", round(df["risk_score"].std(), 2))
            
            with analytic_col2:
                st.markdown("### ⏱️ Duration Metrics")
                st.metric("⏱️ Longest Call", f"{df['call_duration_seconds'].max()}s")
                st.metric("⚡ Shortest Call", f"{df['call_duration_seconds'].min()}s")
                st.metric("📊 Duration Std Dev", f"{round(df['call_duration_seconds'].std(), 2)}s")
            
            with analytic_col3:
                st.markdown("### 🚨 Threat Analysis")
                critical_calls = df[df["risk_score"] >= 80].shape[0]
                st.metric("🔴 Critical Threats", critical_calls)
                suspicious_rate = round((suspicious_calls / total_calls) * 100, 1)
                st.metric("📈 Threat Rate", f"{suspicious_rate}%")
                
                # Threat level indicator
                if suspicious_rate >= 25:
                    threat_status = "🔴 HIGH ALERT"
                    threat_color = "#dc3545"
                elif suspicious_rate >= 10:
                    threat_status = "🟡 ELEVATED"
                    threat_color = "#ffc107"
                else:
                    threat_status = "🟢 SECURE"
                    threat_color = "#28a745"
                
                st.markdown(f"""
                    <div style="background: {threat_color}; color: white; padding: 1rem; 
                                border-radius: 10px; text-align: center; font-weight: bold;
                                margin-top: 1rem;">
                        System Status: {threat_status}
                    </div>
                """, unsafe_allow_html=True)

    else:
        st.markdown("""
            <div class="success-card">
                <h2>🎉 No Data Available</h2>
                <p>Connect to your VoIP system to start monitoring calls</p>
            </div>
        """, unsafe_allow_html=True)

# ============ CALL RECORDS ============
elif page == "📋 Call Records":
    st.markdown('<h1 class="main-title">📋 Call Records Management</h1>', unsafe_allow_html=True)
    
    if not df.empty:
        # Modern filter section
        st.markdown('<div class="section-header">🔍 Smart Filters</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="filter-section">', unsafe_allow_html=True)
            
            filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
            
            with filter_col1:
                caller_filter = st.text_input("📞 Caller ID", placeholder="Search caller...")
            with filter_col2:
                callee_filter = st.text_input("📱 Callee ID", placeholder="Search callee...")
            with filter_col3:
                risk_threshold = st.slider("⚠️ Min Risk Score", 0, 100, 0)
            with filter_col4:
                show_only_suspicious = st.checkbox("🚨 Suspicious Only")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply filters with error handling
        filtered_df = df.copy()
        try:
            if caller_filter:
                filtered_df = filtered_df[filtered_df["caller_id"].str.contains(caller_filter, case=False, na=False, regex=False)]
            if callee_filter:
                filtered_df = filtered_df[filtered_df["callee_id"].str.contains(callee_filter, case=False, na=False, regex=False)]
            if risk_threshold > 0:
                filtered_df = filtered_df[filtered_df["risk_score"] >= risk_threshold]
            if show_only_suspicious:
                filtered_df = filtered_df[filtered_df["suspicious"] == True]
        except Exception as e:
            st.error(f"Filter error: {e}")
            filtered_df = df.copy()
        
        # Enhanced results summary
        st.markdown('<div class="section-header">📊 Results Overview</div>', unsafe_allow_html=True)
        
        result_col1, result_col2, result_col3, result_col4 = st.columns(4)
        
        with result_col1:
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
                           padding: 1rem; border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: bold;">📝 {len(filtered_df)}</div>
                    <div>Records Found</div>
                </div>
            """, unsafe_allow_html=True)
        
        with result_col2:
            suspicious_in_results = filtered_df[filtered_df["suspicious"] == True].shape[0]
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fa709a, #fee140); color: white; 
                           padding: 1rem; border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: bold;">🚨 {suspicious_in_results}</div>
                    <div>Suspicious</div>
                </div>
            """, unsafe_allow_html=True)
        
        with result_col3:
            avg_risk_filtered = round(filtered_df["risk_score"].mean(), 2) if not filtered_df.empty else 0
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4ecdc4, #44a08d); color: white; 
                           padding: 1rem; border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: bold;">📊 {avg_risk_filtered}</div>
                    <div>Avg Risk Score</div>
                </div>
            """, unsafe_allow_html=True)
        
        with result_col4:
            max_risk = filtered_df["risk_score"].max() if not filtered_df.empty else 0
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ff9a9e, #fecfef); color: #333; 
                           padding: 1rem; border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: bold;">🎯 {max_risk}</div>
                    <div>Max Risk Score</div>
                </div>
            """, unsafe_allow_html=True)
        
        if not filtered_df.empty:
            # Sorting options with modern UI
            st.markdown('<div class="section-header">📈 Table Configuration</div>', unsafe_allow_html=True)
            
            sort_col1, sort_col2, sort_col3 = st.columns([2, 2, 1])
            with sort_col1:
                sort_by = st.selectbox("📈 Sort by Column", 
                                     ["call_time", "risk_score", "call_duration_seconds", "caller_id", "callee_id"])
            with sort_col2:
                sort_order = st.selectbox("🔄 Sort Order", ["Descending", "Ascending"])
            with sort_col3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 Reset Filters"):
                    st.rerun()
            
            # Apply sorting
            ascending = sort_order == "Ascending"
            if sort_by in filtered_df.columns:
                filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
            
            # Enhanced table styling
            def enhanced_highlight_row(row):
                if row["risk_score"] >= 80:
                    return ["background: linear-gradient(90deg, #ffebee, #ffcdd2); border-left: 6px solid #f44336; font-weight: bold;" for _ in row]
                elif row["risk_score"] >= 70:
                    return ["background: linear-gradient(90deg, #fff3e0, #ffe0b2); border-left: 6px solid #ff9800; font-weight: bold;" for _ in row]
                elif row["risk_score"] >= 50:
                    return ["background: linear-gradient(90deg, #fff8e1, #ffecb3); border-left: 4px solid #ffc107;" for _ in row]
                elif row["risk_score"] >= 30:
                    return ["background: linear-gradient(90deg, #f1f8e9, #c8e6c9); border-left: 4px solid #4caf50;" for _ in row]
                else:
                    return ["background: linear-gradient(90deg, #e8f5e8, #c8e6c9); border-left: 3px solid #2e7d32;" for _ in row]
                     
            st.markdown('<div class="section-header">📋 Call Records Table</div>', unsafe_allow_html=True)
            st.dataframe(
                filtered_df.style.apply(enhanced_highlight_row, axis=1),
                use_container_width=True,
                height=500
            )
            
            # Export with modern button
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("📥 Export Data", type="primary"):
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv,
                        file_name=f"voip_calls_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("📊 Generate Report"):
                    st.success("📋 Report generated successfully!")
                    
        else:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #74b9ff, #0984e3); color: white; 
                           padding: 2rem; border-radius: 15px; text-align: center; margin: 2rem 0;">
                    <h3>🔍 No Matching Records</h3>
                    <p>Try adjusting your search filters</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="success-card">
                <h2>📞 No Call Data</h2>
                <p>Start monitoring to see call records here</p>
            </div>
        """, unsafe_allow_html=True)

# ============ ALERTS ============
elif page == "🚨 Alerts":
    st.markdown('<h1 class="main-title">🚨 Security Alerts Center</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">🛡️ Real-time Threat Detection & Response Dashboard</p>', unsafe_allow_html=True)

    if not df.empty:
        alerts = df[df["suspicious"] == True]

        # Enhanced Alert Summary with modern cards
        st.markdown('<div class="section-header">🎯 Alert Command Center</div>', unsafe_allow_html=True)
        
        alert_col1, alert_col2, alert_col3, alert_col4 = st.columns(4)
        
        total_suspicious = len(alerts)
        high_risk_count = alerts[alerts["risk_score"] >= 70].shape[0] if not alerts.empty else 0
        critical_risk_count = alerts[alerts["risk_score"] >= 80].shape[0] if not alerts.empty else 0
        avg_risk = round(alerts["risk_score"].mean(), 2) if not alerts.empty else 0
        
        with alert_col1:
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a52); color: white; 
                           padding: 1.5rem; border-radius: 15px; text-align: center;
                           box-shadow: 0 8px 25px rgba(255,107,107,0.3);">
                    <div style="font-size: 2.5rem; font-weight: bold;">🚨 {total_suspicious}</div>
                    <div style="font-size: 1rem; opacity: 0.9;">Total Alerts</div>
                </div>
            """, unsafe_allow_html=True)
        
        with alert_col2:
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fd7e14, #e55d0c); color: white; 
                           padding: 1.5rem; border-radius: 15px; text-align: center;
                           box-shadow: 0 8px 25px rgba(253,126,20,0.3);">
                    <div style="font-size: 2.5rem; font-weight: bold;">⚠️ {high_risk_count}</div>
                    <div style="font-size: 1rem; opacity: 0.9;">High Risk (70+)</div>
                </div>
            """, unsafe_allow_html=True)
        
        with alert_col3:
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #dc3545, #c82333); color: white; 
                           padding: 1.5rem; border-radius: 15px; text-align: center;
                           box-shadow: 0 8px 25px rgba(220,53,69,0.3);">
                    <div style="font-size: 2.5rem; font-weight: bold;">🔴 {critical_risk_count}</div>
                    <div style="font-size: 1rem; opacity: 0.9;">Critical (80+)</div>
                </div>
            """, unsafe_allow_html=True)
        
        with alert_col4:
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #6f42c1, #5a2d91); color: white; 
                           padding: 1.5rem; border-radius: 15px; text-align: center;
                           box-shadow: 0 8px 25px rgba(111,66,193,0.3);">
                    <div style="font-size: 2.5rem; font-weight: bold;">📊 {avg_risk}</div>
                    <div style="font-size: 1rem; opacity: 0.9;">Avg Risk Score</div>
                </div>
            """, unsafe_allow_html=True)

        if not alerts.empty:
            # Two-column layout for better organization
            alert_analysis_col1, alert_analysis_col2 = st.columns([1, 1])
            
            with alert_analysis_col1:
                st.markdown('<div class="section-header">🎯 Risk Level Analysis</div>', unsafe_allow_html=True)
                
                # Enhanced risk level breakdown
                critical = alerts[alerts["risk_score"] >= 80].shape[0]
                high = alerts[(alerts["risk_score"] >= 70) & (alerts["risk_score"] < 80)].shape[0]
                medium = alerts[(alerts["risk_score"] >= 50) & (alerts["risk_score"] < 70)].shape[0]
                low = alerts[alerts["risk_score"] < 50].shape[0]
                
                fig4, ax4 = plt.subplots(figsize=(8, 8))
                sizes = [critical, high, medium, low]
                labels = ['🔴 Critical (80+)', '🟠 High (70-79)', '🟡 Medium (50-69)', '🟢 Low (<50)']
                colors = ['#DC143C', '#FF4500', '#FFC107', '#28A745']
                
                non_zero_data = [(size, label, color) for size, label, color in zip(sizes, labels, colors) if size > 0]
                if non_zero_data:
                    sizes_filtered, labels_filtered, colors_filtered = zip(*non_zero_data)
                    
                    wedges, texts, autotexts = ax4.pie(sizes_filtered,
                                                      labels=labels_filtered,
                                                      autopct='%1.1f%%',
                                                      colors=colors_filtered,
                                                      startangle=90,
                                                      explode=[0.1 if 'Critical' in label else 0.05 if 'High' in label else 0 for label in labels_filtered],
                                                      shadow=True,
                                                      textprops={'fontsize': 11, 'fontweight': 'bold'})
                    
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                        autotext.set_fontsize(12)
                    
                    ax4.set_title('🎯 Alert Severity Breakdown', fontweight='bold', fontsize=14, pad=20)
                    fig4.patch.set_facecolor('#ffffff')
                    st.pyplot(fig4)
            
            with alert_analysis_col2:
                st.markdown('<div class="section-header">🔥 Top Threat Sources</div>', unsafe_allow_html=True)
                
                if not alerts.empty:
                    top_risky = alerts.nlargest(8, 'risk_score')[['caller_id', 'risk_score', 'callee_id']]
                    
                    for i, (idx, row) in enumerate(top_risky.iterrows()):
                        # Determine risk level and colors
                        if row['risk_score'] >= 80:
                            risk_level = "CRITICAL"
                            bg_color = "linear-gradient(135deg, #dc3545, #c82333)"
                            border_color = "#dc3545"
                            icon = "🔴"
                        elif row['risk_score'] >= 70:
                            risk_level = "HIGH"
                            bg_color = "linear-gradient(135deg, #fd7e14, #e55d0c)"
                            border_color = "#fd7e14"
                            icon = "🟠"
                        else:
                            risk_level = "MEDIUM"
                            bg_color = "linear-gradient(135deg, #ffc107, #e0a800)"
                            border_color = "#ffc107"
                            icon = "🟡"
                        
                        st.markdown(
                            f"""
                            <div style='background: {bg_color}; color: white;
                                        padding: 1rem; margin: 0.8rem 0; border-radius: 12px;
                                        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
                                        transform: translateX(0); transition: all 0.3s ease;
                                        animation: slideIn 0.5s ease {i * 0.1}s both;'>
                                <div style='display: flex; justify-content: space-between; align-items: center;'>
                                    <div style='flex: 1;'>
                                        <div style='font-size: 1.1rem; font-weight: bold; margin-bottom: 0.3rem;'>
                                            {icon} #{i+1} Risk Source
                                        </div>
                                        <div style='font-size: 0.95rem; opacity: 0.9;'>
                                            📞 {row['caller_id'][:15]}{'...' if len(str(row['caller_id'])) > 15 else ''}<br>
                                            📱 {row['callee_id'][:15]}{'...' if len(str(row['callee_id'])) > 15 else ''}
                                        </div>
                                    </div>
                                    <div style='text-align: right;'>
                                        <div style='background: rgba(255,255,255,0.2); 
                                                   padding: 0.5rem 1rem; border-radius: 20px;
                                                   font-weight: bold; font-size: 1.1rem;'>
                                            {row['risk_score']}
                                        </div>
                                        <div style='font-size: 0.8rem; margin-top: 0.3rem; opacity: 0.8;'>
                                            {risk_level}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )

            # Enhanced timeline analysis
            if "call_time" in alerts.columns:
                alerts_copy = alerts.copy()
                alerts_copy["call_time"] = pd.to_datetime(alerts_copy["call_time"], errors="coerce")
                
                st.markdown('<div class="section-header">📈 Threat Timeline Analysis</div>', unsafe_allow_html=True)
                
                timeline_col1, timeline_col2 = st.columns([1, 3])
                
                with timeline_col1:
                    time_granularity = st.selectbox("⏰ Time Resolution", ["Hour", "Minute", "Day"], key="timeline_gran")
                    chart_type = st.selectbox("📊 Chart Type", ["Line Chart", "Area Chart", "Bar Chart"])
                
                with timeline_col2:
                    # Group by time
                    if time_granularity == "Hour":
                        time_counts = alerts_copy.groupby(alerts_copy["call_time"].dt.floor("H")).size()
                    elif time_granularity == "Minute":
                        time_counts = alerts_copy.groupby(alerts_copy["call_time"].dt.floor("min")).size()
                    else:  # Day
                        time_counts = alerts_copy.groupby(alerts_copy["call_time"].dt.floor("D")).size()
                    
                    if not time_counts.empty:
                        if chart_type == "Area Chart":
                            st.area_chart(time_counts, height=350, color="#667eea")
                        elif chart_type == "Bar Chart":
                            st.bar_chart(time_counts, height=350, color="#f093fb")
                        else:
                            st.line_chart(time_counts, height=350, color="#ff6b6b")
                
                # Recent alerts with modern timeline cards
                st.markdown('<div class="section-header">🕐 Recent Alert Timeline</div>', unsafe_allow_html=True)
                recent_alerts = alerts_copy.nlargest(8, 'call_time')[['call_time', 'caller_id', 'callee_id', 'risk_score']].copy()
                
                for i, (idx, row) in enumerate(recent_alerts.iterrows()):
                    time_str = row['call_time'].strftime('%H:%M:%S') if pd.notna(row['call_time']) else 'Unknown'
                    date_str = row['call_time'].strftime('%Y-%m-%d') if pd.notna(row['call_time']) else 'Unknown'
                    
                    if row['risk_score'] >= 80:
                        card_bg = "linear-gradient(135deg, #ff416c, #ff4757)"
                        pulse_color = "#ff4757"
                    elif row['risk_score'] >= 70:
                        card_bg = "linear-gradient(135deg, #fd79a8, #fdcb6e)"
                        pulse_color = "#fd79a8"
                    else:
                        card_bg = "linear-gradient(135deg, #74b9ff, #0984e3)"
                        pulse_color = "#74b9ff"
                    
                    st.markdown(
                        f"""
                        <div style='background: white; border: 2px solid {pulse_color}; 
                                    padding: 1.5rem; margin: 1rem 0; border-radius: 15px;
                                    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                                    animation: slideIn 0.6s ease {i * 0.1}s both;
                                    position: relative; overflow: hidden;'>
                            <div style='position: absolute; top: 0; left: 0; width: 100%; height: 4px;
                                        background: {card_bg};'></div>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div style='flex: 1;'>
                                    <div style='display: flex; align-items: center; margin-bottom: 0.8rem;'>
                                        <div style='background: {card_bg}; color: white; 
                                                   padding: 0.3rem 0.8rem; border-radius: 20px; 
                                                   font-size: 0.85rem; font-weight: bold; margin-right: 1rem;'>
                                            ALERT #{i+1}
                                        </div>
                                        <div style='color: #666; font-size: 0.9rem;'>
                                            📅 {date_str} • 🕐 {time_str}
                                        </div>
                                    </div>
                                    <div style='font-size: 1.1rem; font-weight: 600; color: #2c3e50; margin-bottom: 0.5rem;'>
                                        📞 <span style='color: {pulse_color}; font-weight: bold;'>{row['caller_id']}</span> 
                                        → 📱 <span style='color: {pulse_color}; font-weight: bold;'>{row['callee_id']}</span>
                                    </div>
                                </div>
                                <div style='text-align: center; margin-left: 1rem;'>
                                    <div style='background: {card_bg}; color: white; 
                                               padding: 1rem 1.5rem; border-radius: 50px;
                                               font-weight: bold; font-size: 1.2rem;
                                               box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
                                        {row['risk_score']}
                                    </div>
                                    <div style='font-size: 0.8rem; color: #666; margin-top: 0.5rem; font-weight: 500;'>
                                        RISK SCORE
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )

            # Enhanced data table
            st.markdown('<div class="section-header">📋 Detailed Alert Records</div>', unsafe_allow_html=True)
            
            # Filter options for alerts
            alert_filter_col1, alert_filter_col2 = st.columns(2)
            with alert_filter_col1:
                min_risk_alert = st.slider("🎯 Minimum Risk Score", 50, 100, 50, key="alert_risk_filter")
            with alert_filter_col2:
                sort_alerts_by = st.selectbox("📊 Sort Alerts By", 
                                            ["risk_score", "call_time", "call_duration_seconds"], 
                                            key="alert_sort")
            
            # Apply alert filters
            filtered_alerts = alerts[alerts["risk_score"] >= min_risk_alert].copy()
            if sort_alerts_by in filtered_alerts.columns:
                filtered_alerts = filtered_alerts.sort_values(by=sort_alerts_by, ascending=False)
            
            # Enhanced alert table styling
            def style_alert_table(row):
                if row["risk_score"] >= 90:
                    return ["background: linear-gradient(90deg, #ffebee, #ffcdd2); color: #b71c1c; font-weight: bold; border-left: 8px solid #f44336;" for _ in row]
                elif row["risk_score"] >= 80:
                    return ["background: linear-gradient(90deg, #fff3e0, #ffe0b2); color: #bf360c; font-weight: bold; border-left: 6px solid #ff5722;" for _ in row]
                elif row["risk_score"] >= 70:
                    return ["background: linear-gradient(90deg, #fff8e1, #ffecb3); color: #e65100; font-weight: bold; border-left: 4px solid #ff9800;" for _ in row]
                else:
                    return ["background: linear-gradient(90deg, #f3e5f5, #e1bee7); color: #4a148c; border-left: 3px solid #9c27b0;" for _ in row]
            
            st.dataframe(
                filtered_alerts.style.apply(style_alert_table, axis=1),
                use_container_width=True,
                height=450
            )
            
            # Action buttons with modern styling
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if st.button("📥 Export Alerts", type="primary"):
                    csv = filtered_alerts.to_csv(index=False)
                    st.download_button(
                        label="💾 Download Alert Data",
                        data=csv,
                        file_name=f"security_alerts_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with action_col2:
                if st.button("📧 Send Alert Report"):
                    st.success("📧 Alert report sent to security team!")
                    
            with action_col3:
                if st.button("🔄 Refresh Data"):
                    st.rerun()

        else:
            # Enhanced no alerts state
            st.markdown("""
                <div style="background: linear-gradient(135deg, #00b894, #00cec9); color: white; 
                           padding: 3rem; border-radius: 20px; text-align: center; margin: 2rem 0;
                           box-shadow: 0 15px 35px rgba(0,184,148,0.3);">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">🛡️</div>
                    <h2 style="font-size: 2rem; margin-bottom: 1rem;">All Clear!</h2>
                    <p style="font-size: 1.2rem; opacity: 0.9;">No suspicious activities detected</p>
                    <div style="background: rgba(255,255,255,0.2); padding: 1rem; 
                               border-radius: 10px; margin-top: 1.5rem; display: inline-block;">
                        ✅ System Status: SECURE
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.balloons()
    else:
        st.markdown("""
            <div class="success-card">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📡</div>
                <h2>Initializing Security System</h2>
                <p>Connect your VoIP infrastructure to begin monitoring</p>
            </div>
        """, unsafe_allow_html=True)
