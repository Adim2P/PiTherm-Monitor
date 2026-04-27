import os
import time
import threading
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font
from src.pitherm.smtp_client import SMTPClient
from email.mime.application import MIMEApplication
import csv

_last_report_week = None
_excel_lock = threading.Lock()
BASE_LOG_DIR = "logs"
CURRENT_DIR = os.path.join(BASE_LOG_DIR, "current")
ARCHIVE_DIR = os.path.join(BASE_LOG_DIR, "archive")
_TEST_MODE = False
_FORCE_CSV_FALLBACK = False

def log_to_csv_fallback(temp, hum):
    ensure_log_directories()

    year, week, _ = datetime.now().isocalendar()
    week_str = f"{year}_W{week:02d}"

    fallback_file = os.path.join(CURRENT_DIR, f"fallback_{week_str}.csv")
    now = datetime.now()
    file_exists = os.path.exists(fallback_file)

    with open(fallback_file, mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Date", 
                "Time", 
                "Temperature (°C)", 
                "Humidity (%)"
            ])

        writer.writerow([
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M:%S"),
            temp,
            hum
        ])
    print("[FALLBACK] Logged reading to CSV.")

def ensure_log_directories():
    os.makedirs(CURRENT_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

def archive_old_logs():
    ensure_log_directories()

    current_year, current_week, _ = datetime.now().isocalendar()
    current_week_str = f"{current_year}_W{current_week:02d}"

    for file in os.listdir(CURRENT_DIR):
        if file.startswith("temp_log_") and file.endswith(".xlsx"):
            file_week = file.replace("temp_log_", "").replace(".xlsx", "")

            if file_week != current_week_str:
                src_path = os.path.join(CURRENT_DIR, file)
                dst_path = os.path.join(ARCHIVE_DIR, file)

                if not os.path.exists(dst_path):
                    os.rename(src_path, dst_path)
                    print(f"[ARCHIVE] Moved {file} to archive.")

def log_to_excel(temp, hum):
    ensure_log_directories()

    with _excel_lock:
        archive_old_logs()

        year, week, _ = datetime.now().isocalendar()
        filename = os.path.join(CURRENT_DIR, f"temp_log_{year}_W{week:02d}.xlsx")

        #*CSV Fallback Test Snippet
        if _TEST_MODE and _FORCE_CSV_FALLBACK:
            print("[TEST] Forcing CSV Fallback...")
            log_to_csv_fallback(temp, hum)
            return
        
        try:
            try:
                wb = load_workbook(filename)
                ws = wb.active
            except FileNotFoundError:
                wb = Workbook()
                ws = wb.active
                ws.title = "Weekly Readings"
                ws.append(["Date", "Time", "Temperature (°C)", "Humidity (%)"])
                for col in range(1, 5):
                    ws[f"{get_column_letter(col)}1"].font = Font(bold=True)
            now = datetime.now()
            ws.append([
                now.strftime("%Y-%m-%d"), 
                now.strftime("%H:%M:%S"), 
                temp, 
                hum
            ])
            wb.save(filename)
        except Exception as e:
            print("[CRITICAL] Excel logging failed. Switching to CSV Fallback:", e)
            log_to_csv_fallback(temp, hum)

def send_monthly_report():
    with _excel_lock:

        year, week, _ = datetime.now().isocalendar()
        week_str = f"{year}_W{week:02d}"
        filename = os.path.join(CURRENT_DIR, f"temp_log_{week_str}.xlsx")

    #*Test Snippet for Sending of Weekly Email
    if _TEST_MODE:
        print(f"[TEST] Would send weekly report: {filename}")
        print(f"[TEST] Subject: Weekly Temp Report - {week_str}")
        return

    if not os.path.exists(filename):
        print("[WARN] No Excel File to send.")
        return

    subject = f"Weekly Temp Report - {week_str}"
    body = f"""
    <p>Attached is the temperature and humidity log for {week_str}.</p>
    <p>- Raspberry Pi Monitor</p>
    """

    with open(filename, 'rb') as f:
        attachment = MIMEApplication(
            f.read(),
            _subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        attachment.add_header(
            'Content-Disposition',
            'attachment',
            filename=filename
        )
    
    SMTPClient().send(
        subject, 
        body, 
        is_html=True, 
        attachment=attachment
    )

def check_and_send_monthly_report(now=None):
    global _last_report_week

    if now is None:
        now = datetime.now()
        
    current_week = now.isocalendar()[:2]

    if now.weekday() == 0 and now.hour >= 7 and _last_report_week != current_week:
            send_monthly_report()
            _last_report_week = current_week

def run_scheduler():
    while True:
        check_and_send_monthly_report()
        time.sleep(60)

def start_scheduler():
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()