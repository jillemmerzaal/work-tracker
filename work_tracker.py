
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

# Constants
CSV_FILE = "work_log.csv"
PAY_PERIOD_START = datetime(2025, 9, 8).date()
PAY_PERIOD_LENGTH = 14
TARGET_HOURS = 60

# Load existing data
try:
    df = pd.read_csv(CSV_FILE, parse_dates=["Date"])
except FileNotFoundError:
    df = pd.DataFrame(columns=["Date", "Start Time", "End Time", "Break Start", "Break End", "Work Duration (hrs)"])

# Title
st.title("Work Time Tracker")

# Input form
st.subheader("Log New Work Entry")
with st.form("log_form"):
    date = st.date_input("Date")
    start_time = st.time_input("Start Time", value=time(9,0))
    end_time = st.time_input("End Time", value=time(16,0))
    break_start = st.time_input("Break Start", value=time(0,0))
    break_end = st.time_input("Break End", value=time(0,0))
    submitted = st.form_submit_button("Log Work")

    if submitted:
        start_dt = datetime.combine(date, start_time)
        end_dt = datetime.combine(date, end_time)
        break_start_dt = datetime.combine(date, break_start)
        break_end_dt = datetime.combine(date, break_end)
        work_duration = (end_dt - start_dt - (break_end_dt - break_start_dt)).total_seconds() / 3600

        new_entry = {
            "Date": date,
            "Start Time": start_time.strftime("%H:%M"),
            "End Time": end_time.strftime("%H:%M"),
            "Break Start": break_start.strftime("%H:%M"),
            "Break End": break_end.strftime("%H:%M"),
            "Work Duration (hrs)": round(work_duration, 2)
        }

        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success(f"Logged {round(work_duration, 2)} hours for {date}")

# Reverse order of logs
df = df.sort_values(by="Date", ascending=False)

# Display logs
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

# Summary of completed pay periods
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
