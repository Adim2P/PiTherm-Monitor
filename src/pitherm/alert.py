from src.pitherm.smtp_newClient import SMTPClient

def send_email_alert(temp, hum, alert_type="high"):
    subject = "ALERT: High Temperature" if alert_type == "high" else "ALERT: Low temperature"

    body = f"""
Server Room Temperature Alert:

Temperature: {temp:.1f}°C
Humidity: {hum:.1f}%

- Raspberry Pi Temperature Monitor
"""
    SMTPClient().send(subject, body)