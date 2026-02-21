import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.pitherm.config import (
    SMTP_USER,
    SMTP_PASS,
    SMTP_RECIPIENT,
    SMTP_CC
)

def build_recipients(primary):
    cc_list = [e.strip() for e in SMTP_CC.split(",")] if SMTP_CC else []
    return primary, cc_list, [primary] + cc_list

def send_email_alert(temp, hum, alert_type="high"):
    smtp_host = 'smtp2.agmstech.com'
    smtp_port = 587
    sender = SMTP_USER

    primary_to, cc_list, recipients = build_recipients(SMTP_RECIPIENT)
    subject = "ALERT: High temperature" if alert_type == "high" else "ALERT: Low temperature"
    
    body = f"""
    Server Room Temperature Alert:

    Temperature: {temp:.1f}°C
    Humidity: {hum:.1f}%

    - Raspberry Pi Temperature Monitor
    """
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = primary_to
    if cc_list:
        msg['Cc'] = ", ".join(cc_list)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=5)
        server.starttls()
        server.login(sender, SMTP_PASS)
        server.sendmail(sender, recipients, msg.as_string())
        server.quit()
        print("[OK] Email alert sent via SMTP.")
    except Exception as err:
        print("[ERROR] Failed to send email:", err)

