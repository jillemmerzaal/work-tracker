import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Constants
CSV_FILE = "work_log.csv"
PAY_PERIOD_START = datetime(2025, 9, 8).date()
PAY_PERIOD_LENGTH = 14
TARGET_HOURS = 60

# Load work log
try:
    df = pd.read_csv(CSV_FILE, parse_dates=["Date"])
except FileNotFoundError:
    df = pd.DataFrame(columns=["Date", "Start Time", "End Time", "Break Start", "Break End", "Work Duration (hrs)"])

# Reverse order of logs (newest first)
df = df.sort_values(by="Date", ascending=False)

# Display logs
st.title("Work Time Tracker")
st.subheader("Logged Work Entries (Newest First)")
st.dataframe(df)

# Determine current pay period
today = datetime.now().date()
days_since_start = (today - PAY_PERIOD_START).days
current_period_index = days_since_start // PAY_PERIOD_LENGTH
current_period_start = PAY_PERIOD_START + timedelta(days=current_period_index * PAY_PERIOD_LENGTH)
current_period_end = current_period_start + timedelta(days=PAY_PERIOD_LENGTH - 1)

# Filter current pay period
current_period_df = df[(df["Date"] >= pd.Timestamp(current_period_start)) & (df["Date"] <= pd.Timestamp(current_period_end))]
current_total_hours = current_period_df["Work Duration (hrs)"].sum()
current_overtime = current_total_hours - TARGET_HOURS

st.subheader("Current Pay Period Summary")
st.write(f"**Period:** {current_period_start} to {current_period_end}")
st.write(f"**Total Hours:** {round(current_total_hours, 2)}")
st.write(f"**Overtime:** {round(current_overtime, 2)} hours")

# Summary of all completed pay periods
completed_periods = []
for i in range(current_period_index):
    period_start = PAY_PERIOD_START + timedelta(days=i * PAY_PERIOD_LENGTH)
    period_end = period_start + timedelta(days=PAY_PERIOD_LENGTH - 1)
    period_df = df[(df["Date"] >= pd.Timestamp(period_start)) & (df["Date"] <= pd.Timestamp(period_end))]
    total_hours = period_df["Work Duration (hrs)"].sum()
    overtime = total_hours - TARGET_HOURS
    completed_periods.append({
        "Period Start": period_start,
        "Period End": period_end,
        "Total Hours": round(total_hours, 2),
        "Overtime": round(overtime, 2)
    })

if completed_periods:
    st.subheader("Summary of Completed Pay Periods")
    summary_df = pd.DataFrame(completed_periods)
    st.dataframe(summary_df)

# Export button
st.subheader("Export Work Log")
csv_data = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download work_log.csv",
    data=csv_data,
    file_name="work_log.csv",
    mime="text/csv"
)