import pandas as pd
import tkinter as tk
from tkinter import messagebox

# Load your CSV (use the path you have)
df = pd.read_csv(r"C:\Users\istut\OneDrive\Desktop\VoIPGuard\VoIPGuard\CDR_.csv")

# Initialize tkinter root
root = tk.Tk()
root.withdraw()  # hide the main window

# Iterate through the calls
for index, call in df.iterrows():
    if call['is_blacklisted']:  # check if call is blacklisted
        messagebox.showwarning(
            "VoIP Guard Alert",
            f"Blacklisted call detected!\nCaller ID: {call['caller_id']}\nCallee ID: {call['callee_id']}"
        )