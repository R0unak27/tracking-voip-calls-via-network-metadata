import pandas as pd

df = pd.read_csv("C:/Users/istut/OneDrive/Desktop/VoIPGuard/VoIPGuard/CDR_.csv")

print(df.head())
print(df.shape)

# Check for missing values
print(df.isnull().sum())

# Check data types
print(df.dtypes)

df['call_start_time'] = pd.to_datetime(df['call_start_time'], format='%H:%M:%S')
df['call_duration_seconds'] = pd.to_numeric(df['call_duration_seconds'])
df['call_quality'] = pd.to_numeric(df['call_quality'])
df['is_blacklisted'] = df['is_blacklisted'].astype(bool)

print(df['call_type'].value_counts())
print(df['call_status'].value_counts())
print(df['call_duration_seconds'].mean())
print(df[df['is_blacklisted'] == True])

alerts = df[(df['is_blacklisted'] == True) | 
            (df['call_quality'] < 2) |
            ((df['call_duration_seconds'] > 300) & (df['caller_location'] != 'India'))]

print(alerts)

import pandas as pd

# Load your CSV
df = pd.read_csv(r"C:/Users/istut/OneDrive/Desktop/VoIPGuard/VoIPGuard/CDR_.csv")

# Set threshold for high-frequency calls
high_freq_threshold = 100

# Flag suspicious calls
suspicious_calls = df[
    (df['is_blacklisted'] == True) |
    (df['call_status'] != 'completed') |
    (df['call_quality'] < 2) |
    (df['number_of_previous_calls'] > high_freq_threshold)
]

# Optional: add a column explaining why each call is flagged
def flag_reason(row):
    reasons = []
    if row['is_blacklisted']:
        reasons.append("Blacklisted")
    if row['call_status'] != 'completed':
        reasons.append(f"Call {row['call_status']}")
    if row['call_quality'] < 2:
        reasons.append(f"Low quality ({row['call_quality']})")
    if row['number_of_previous_calls'] > high_freq_threshold:
        reasons.append(f"High freq ({row['number_of_previous_calls']})")
    return ", ".join(reasons)

suspicious_calls['flag_reason'] = suspicious_calls.apply(flag_reason, axis=1)

# Show the flagged calls
print(suspicious_calls)

# Optional: save to CSV
suspicious_calls.to_csv("C:/Users/istut/OneDrive/Desktop/VoIPGuard/VoIPGuard/suspicious_calls.csv", index=False)

# Filter only blacklisted calls
blacklisted_calls = df[df['is_blacklisted'] == True]

# Show the first few blacklisted calls
print(blacklisted_calls.head())

# How many blacklisted calls are there
print("Total blacklisted calls:", blacklisted_calls.shape[0])

# Top blacklisted callers
top_blacklisted_callers = blacklisted_calls['caller_id'].value_counts().head(10)
print("Top blacklisted callers:\n", top_blacklisted_callers)

# Blacklisted calls by caller location
blacklisted_by_location = blacklisted_calls['caller_location'].value_counts()
print("\nBlacklisted calls by location:\n", blacklisted_by_location)

# Blacklisted calls by call type (inbound/outbound)
blacklisted_by_type = blacklisted_calls['call_type'].value_counts()
print("\nBlacklisted calls by call type:\n", blacklisted_by_type)

# Average call duration of blacklisted calls
avg_duration_blacklisted = blacklisted_calls['call_duration_seconds'].mean()
print("\nAverage duration of blacklisted calls:", avg_duration_blacklisted, "seconds")

# Criteria for suspicious calls
# 1. Low call quality (say < 2.5)
# 2. Failed or dropped calls
# 3. High number of previous calls (say > 100)

suspicious_calls = df[
    (df['call_quality'] < 2.5) |
    (df['call_status'].isin(['failed', 'dropped'])) |
    (df['number_of_previous_calls'] > 100)
]

print("Suspicious calls detected:", len(suspicious_calls))
print(suspicious_calls[['caller_id', 'callee_id', 'call_status', 'call_quality', 'number_of_previous_calls']])

# Filter blacklisted calls
blacklisted_calls = df[df['is_blacklisted'] == True]

print("Blacklisted calls detected:", len(blacklisted_calls))
print(blacklisted_calls[['caller_id', 'callee_id', 'call_status', 'call_quality']])

# Combine both criteria
alerts = pd.concat([suspicious_calls, blacklisted_calls]).drop_duplicates()

print("Total calls to alert:", len(alerts))
print(alerts[['caller_id', 'callee_id', 'call_status', 'call_quality', 'number_of_previous_calls', 'is_blacklisted']])

# Save alerts to a new CSV file for reporting
alerts.to_csv("VoIP_alerts.csv", index=False)
print("Alerts saved to VoIP_alerts.csv")
# Count alerts by type
print("Alerts by call_status:")
print(alerts['call_status'].value_counts())

print("\nAlerts by caller location:")
print(alerts['caller_location'].value_counts())

print("\nAlerts by callee location:")
print(alerts['callee_location'].value_counts())

import pandas as pd
import tkinter as tk
from tkinter import messagebox
import winsound

def show_alert(caller_id, callee_id):
    root = tk.Tk()
    root.withdraw()
    winsound.Beep(1000, 500)  # beep sound
    messagebox.showwarning(
        "VoIP Guard Alert",
        f"Blacklisted call detected!\nCaller ID: {caller_id}\nCallee ID: {callee_id}"
    )

# Load CSV
df = pd.read_csv("C:/Users/istut/OneDrive/Desktop/VoIPGuard/VoIPGuard/CDR_.csv")
blacklisted_calls = df[df['is_blacklisted']]

# Limit to first 10 blacklisted calls
for index, call in blacklisted_calls.head(10).iterrows():
    show_alert(call['caller_id'], call['callee_id'])
