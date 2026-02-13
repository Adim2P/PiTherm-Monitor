import time
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import os
from dotenv import load_dotenv
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font
import schedule
import threading
import json
from src.pitherm.config import (
    THINGSPEAK_API_KEY,
    SMTP_USER,
    SMTP_PASS,
    SMTP_RECIPIENT,
    SMTP_CC,
    TEMP_THRESHOLD_HIGH,
    TEMP_THRESHOLD_LOW
)
from src.pitherm.hardware import HardwareController
from src.pitherm.alert import (
    send_email_alert,
    build_recipients
)
from src.pitherm.logging_service import (
    log_to_excel,
    start_scheduler
)

# === Hardware Setup ===

alert_sent_high = False
alert_sent_low = False

def send_to_thingspeak(temp, hum):
    url = "https://api.thingspeak.com/update"
    params = {'api_key': THINGSPEAK_API_KEY, 'field1': temp, 'field2': hum}
    try:
        r = requests.get(url, params=params)
        print("[UPLOAD] Data sent to ThingSpeak." if r.status_code == 200 and r.text != '0' else f"[WARN] ThingSpeak error: {r.text}")
    except Exception as err:
        print("[ERROR] ThingSpeak exception:", err)

# === Excel Logging ===
def log_to_excel(temp, hum):
    date_str = datetime.now().strftime("%Y-%m")
    filename = f"temp_log_{date_str}.xlsx"
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
    ws.append([now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), temp, hum])
    wb.save(filename)

def send_monthly_report():
    month_str = datetime.now().strftime("%Y-%m")
    filename = f"temp_log_{month_str}.xlsx"
    if not os.path.exists(filename):
        print("[WARN] No Excel file to send.")
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
        attachment = MIMEApplication(f.read(), _subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(attachment)

    try:
        server = smtplib.SMTP('smtp2.agmstech.com', 587)
        server.starttls()
        server.login(sender, SMTP_PASS)
        server.sendmail(sender, recipients, msg.as_string())
        server.quit()
        print("[OK] Monthly Excel report sent via email.")
    except Exception as err:
        print("[ERROR] Failed to send Excel report:", err)

# === Monthly Scheduler ===
def check_and_send_monthly_report():
    now = datetime.now()
    if now.day == 1 and now.hour == 7 and now.minute == 0: #send temp log every 1st of the month at 7:00am
        send_monthly_report()

def run_scheduler():
    while True:
        check_and_send_monthly_report()
        schedule.run_pending()
        time.sleep(60)

start_scheduler()

hardware = HardwareController()

# === Main Loop ===
try:
    print("[START] Monitoring started. Press Ctrl+C to stop.")
    while True:
        try:
            temperature, humidity = hardware.read_sensor()

            if temperature is not None and humidity is not None:
                print(f"[DATA] Temp: {temperature:.1f}°C | Humidity: {humidity:.1f}%")

                hardware.update_lcd(temperature, humidity)

                log_to_excel(temperature, humidity)
                send_to_thingspeak(temperature, humidity)

                if temperature >= TEMP_THRESHOLD_HIGH:
                    print("[DEBUG] High temp alert triggered!")
                    hardware.set_led(True)
                    if not alert_sent_high:
                        send_email_alert(temperature, humidity, alert_type="high")
                        alert_sent_high = True
                        alert_sent_low = False
                elif temperature <= TEMP_THRESHOLD_LOW:
                    print("[DEBUG] Low temp alert triggered!")
                    hardware.set_led(True)
                    if not alert_sent_low:
                        send_email_alert(temperature, humidity, alert_type="low")
                        alert_sent_low = True
                        alert_sent_high = False
                else:
                    hardware.set_led(False)
                    alert_sent_high = False
                    alert_sent_low = False
            else:
                print("[WARN] Sensor read failed.")
        except RuntimeError as err:
            print(f"[ERROR] DHT read error: {err.args[0]}")
        time.sleep(30)

except KeyboardInterrupt:
    print("\n[STOP] Monitoring stopped by user.")

finally:
    hardware.cleanup()
