import os
import time
import threading
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from src.pitherm.config import (
    SMTP_USER,
    SMTP_PASS,
    SMTP_RECIPIENT,
    SMTP_CC
)

_last_report_month = None
_excel_lock = threading.Lock()
BASE_LOG_DIR = "logs"
CURRENT_DIR = os.path.join(BASE_LOG_DIR, "current")
ARCHIVE_DIR = os.path.join(BASE_LOG_DIR, "archive")

def ensure_log_directories():
    os.makedirs(CURRENT_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

def archive_old_logs():
    ensure_log_directories()

    current_month = datetime.now().strftime("%Y-%m")

    for file in os.listdir(CURRENT_DIR):
        if file.startswith("temp_log_") and file.endswith(".xlsx"):
            file_month = file.replace("temp_log_", "").replace(".xlsx", "")

            if file_month != current_month:
                src_path = os.path.join(CURRENT_DIR, file)
                dst_path = os.path.join(ARCHIVE_DIR, file)

                if not os.path.exists(dst_path):
                    os.rename(src_path, dst_path)
                    print(f"[ARCHIVE] Moved {file} to archive.")

def build_recipients(primary):
    cc_list = [e.strip() for e in SMTP_CC.split(",")] if SMTP_CC else []
    return primary, cc_list, [primary] + cc_list

def log_to_excel(temp, hum):
    ensure_log_directories()
    

    with _excel_lock:
        archive_old_logs()

        date_str = datetime.now().strftime("%Y-%m")
        filename = os.path.join(CURRENT_DIR, f"temp_log_{date_str}.xlsx")

    try:
        wb = load_workbook(filename)
        ws = wb.active
    except FileNotFoundError:
        wb = Workbook()
        ws = wb.active
        ws.title = "Monthly Readings"
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

def send_montly_report():
    with _excel_lock:
        month_str = datetime.now().strftime("%Y-%m")
        filename = f"temp_log_{month_str}.xlsx"

    if not os.path.exists(filename):
        print("[WARN] No Excel File to send.")
        return
    
    sender = SMTP_USER
    primary_to, cc_list, recipients = build_recipients(SMTP_RECIPIENT)

    subject = f"Monthly Temp Report - {month_str}"
    body = f"Attached is the temperature and humidity log for {month_str}.\n\n- Raspberry Pi Monitor"

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = primary_to
    if cc_list:
        msg['Cc'] = ", ".join(cc_list)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with open(filename, 'rb') as f:
        attachment = MIMEApplication(
            f.read(),
            _subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(attachment)
    
    try:
        server = smtplib.SMTP('smtp2.agmstech.com', 587)
        server.starttls()
        server.login(sender, SMTP_PASS)
        server.sendmail(sender, recipients, msg.as_strings())
        server.quit()
        print("[OK] Monthly Excel report send via email.")
    except Exception as err:
        print("[ERROR] Failed to send excel report:", err)

def check_and_send_monthly_report():
    global _last_report_month

    now = datetime.now()
    current_month = now.strftime("%Y-%m")

    if now.day == 1 and now.hour >= 7 and _last_report_month != current_month:
            send_montly_report()
            _last_report_month = current_month

def run_scheduler():
    while True:
        check_and_send_monthly_report()
        time.sleep(60)

def start_scheduler():
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()