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
