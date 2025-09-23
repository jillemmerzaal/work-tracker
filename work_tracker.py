import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

CSV_FILE = "work_log.csv"
FIXED_START_DATE = datetime(2025, 1, 1).date()
PERIOD_LENGTH_DAYS = 14
TARGET_HOURS = 60

# Initialize CSV file if it doesn't exist
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["Date", "Start Time", "End Time", "Break Start", "Break End", "Work Duration (hrs)"])
    df_init.to_csv(CSV_FILE, index=False)

# Load existing data
df = pd.read_csv(CSV_FILE)

st.title("Work Time Tracker")

# Input form
with st.form("work_form"):
    date = st.date_input("Date", value=datetime.now().date())
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    break_start = st.time_input("Break Start")
    break_end = st.time_input("Break End")
    submitted = st.form_submit_button("Log Work")

    if submitted:
        start_dt = datetime.combine(date, start_time)
        end_dt = datetime.combine(date, end_time)
        break_start_dt = datetime.combine(date, break_start)
        break_end_dt = datetime.combine(date, break_end)

        work_duration = (end_dt - start_dt - (break_end_dt - break_start_dt)).total_seconds() / 3600

        new_entry = pd.DataFrame({
            "Date": [date.strftime("%Y-%m-%d")],
            "Start Time": [start_time.strftime("%H:%M")],
            "End Time": [end_time.strftime("%H:%M")],
            "Break Start": [break_start.strftime("%H:%M")],
            "Break End": [break_end.strftime("%H:%M")],
            "Work Duration (hrs)": [round(work_duration, 2)]
        })

        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success(f"Logged {round(work_duration, 2)} hours for {date.strftime('%Y-%m-%d')}")

# Function to get current pay period
def get_current_pay_period():
    today = datetime.now().date()
    days_since_start = (today - FIXED_START_DATE).days
    period_index = days_since_start // PERIOD_LENGTH_DAYS
    period_start = FIXED_START_DATE + timedelta(days=period_index * PERIOD_LENGTH_DAYS)
    period_end = period_start + timedelta(days=PERIOD_LENGTH_DAYS - 1)
    return period_start, period_end

# Show current pay period summary
period_start, period_end = get_current_pay_period()
df["Date"] = pd.to_datetime(df["Date"]).dt.date
current_period_df = df[(df["Date"] >= period_start) & (df["Date"] <= period_end)]
total_hours = current_period_df["Work Duration (hrs)"].sum()
overtime = total_hours - TARGET_HOURS

st.subheader("Current Pay Period Summary")
st.markdown(f"**Period:** {period_start} to {period_end}")
st.markdown(f"**Total Hours:** {round(total_hours, 2)}")
st.markdown(f"**Overtime:** {round(overtime, 2)} hours")

# Show history of past pay periods
st.subheader("Pay Period History")
days_since_start = (datetime.now().date() - FIXED_START_DATE).days
num_periods = days_since_start // PERIOD_LENGTH_DAYS + 1

for i in range(num_periods):
    p_start = FIXED_START_DATE + timedelta(days=i * PERIOD_LENGTH_DAYS)
    p_end = p_start + timedelta(days=PERIOD_LENGTH_DAYS - 1)
    period_df = df[(df["Date"] >= p_start) & (df["Date"] <= p_end)]
    p_hours = period_df["Work Duration (hrs)"].sum()
    p_overtime = p_hours - TARGET_HOURS

    with st.expander(f"Period {i+1}: {p_start} to {p_end}"):
        st.write(f"Total Hours: {round(p_hours, 2)}")
        st.write(f"Overtime: {round(p_overtime, 2)} hours")
        st.dataframe(period_df)
