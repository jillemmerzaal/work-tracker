import tkinter as tk
from tkinter import messagebox, Toplevel, Text
from datetime import datetime, timedelta
import csv
import os

CSV_FILE = "work_log.csv"
FIXED_START_DATE = datetime(2025, 1, 1).date()
PERIOD_LENGTH_DAYS = 14
TARGET_HOURS = 60

# Ensure CSV file exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Start Time", "End Time", "Break Start", "Break End", "Work Duration (hrs)"])

# Function to calculate work duration and save to CSV
def log_work():
    try:
        date = datetime.strptime(entry_date.get(), "%Y-%m-%d").date()
        start = datetime.strptime(entry_start.get(), "%H:%M")
        end = datetime.strptime(entry_end.get(), "%H:%M")
        break_start = datetime.strptime(entry_break_start.get(), "%H:%M")
        break_end = datetime.strptime(entry_break_end.get(), "%H:%M")

        work_duration = (end - start - (break_end - break_start)).total_seconds() / 3600

        with open(CSV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([date, entry_start.get(), entry_end.get(), entry_break_start.get(), entry_break_end.get(), round(work_duration, 2)])

        messagebox.showinfo("Success", f"Work duration logged: {round(work_duration, 2)} hours")
        update_summary()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to determine current pay period range
def get_current_pay_period():
    today = datetime.now().date()
    days_since_start = (today - FIXED_START_DATE).days
    period_index = days_since_start // PERIOD_LENGTH_DAYS
    period_start = FIXED_START_DATE + timedelta(days=period_index * PERIOD_LENGTH_DAYS)
    period_end = period_start + timedelta(days=PERIOD_LENGTH_DAYS - 1)
    return period_start, period_end

# Function to calculate total hours in current pay period
def update_summary():
    total_hours = 0
    period_start, period_end = get_current_pay_period()

    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            log_date = datetime.strptime(row["Date"], "%Y-%m-%d").date()
            if period_start <= log_date <= period_end:
                total_hours += float(row["Work Duration (hrs)"])

    overtime = total_hours - TARGET_HOURS
    summary_label.config(text=f"Pay Period: {period_start} to {period_end}\nTotal hours: {round(total_hours, 2)}\nOvertime: {round(overtime, 2)} hours")

# Function to show history of past pay periods
def show_history():
    history_window = Toplevel(root)
    history_window.title("Pay Period History")
    text_area = Text(history_window, width=60, height=30)
    text_area.pack()

    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        logs = [row for row in reader]

    today = datetime.now().date()
    days_since_start = (today - FIXED_START_DATE).days
    current_period_index = days_since_start // PERIOD_LENGTH_DAYS

    for i in range(current_period_index + 1):
        period_start = FIXED_START_DATE + timedelta(days=i * PERIOD_LENGTH_DAYS)
        period_end = period_start + timedelta(days=PERIOD_LENGTH_DAYS - 1)
        period_hours = 0

        for row in logs:
            log_date = datetime.strptime(row["Date"], "%Y-%m-%d").date()
            if period_start <= log_date <= period_end:
                period_hours += float(row["Work Duration (hrs)"])

        overtime = period_hours - TARGET_HOURS
        text_area.insert(tk.END, f"Period {i+1}: {period_start} to {period_end}\n")
        text_area.insert(tk.END, f"  Total Hours: {round(period_hours, 2)}\n")
        text_area.insert(tk.END, f"  Overtime: {round(overtime, 2)} hours\n\n")

# GUI setup
root = tk.Tk()
root.title("Work Time Tracker")

# Input fields
tk.Label(root, text="Date (YYYY-MM-DD)").grid(row=0, column=0)
entry_date = tk.Entry(root)
entry_date.grid(row=0, column=1)

tk.Label(root, text="Start Time (HH:MM)").grid(row=1, column=0)
entry_start = tk.Entry(root)
entry_start.grid(row=1, column=1)

tk.Label(root, text="End Time (HH:MM)").grid(row=2, column=0)
entry_end = tk.Entry(root)
entry_end.grid(row=2, column=1)

tk.Label(root, text="Break Start (HH:MM)").grid(row=3, column=0)
entry_break_start = tk.Entry(root)
entry_break_start.grid(row=3, column=1)

tk.Label(root, text="Break End (HH:MM)").grid(row=4, column=0)
entry_break_end = tk.Entry(root)
entry_break_end.grid(row=4, column=1)

# Buttons
tk.Button(root, text="Log Work", command=log_work).grid(row=5, column=0, columnspan=2)
tk.Button(root, text="View History", command=show_history).grid(row=6, column=0, columnspan=2)

# Summary label
summary_label = tk.Label(root, text="")
summary_label.grid(row=7, column=0, columnspan=2)
update_summary()

root.mainloop()
