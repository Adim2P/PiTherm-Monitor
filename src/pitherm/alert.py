from src.pitherm.smtp_client import SMTPClient

def send_email_alert(temp, hum, alert_type="high"):
    SUBJECT_MAP = {
        "high": "ALERT: High Temperature",
        "low": "ALERT: Low Temperature",
        "recovered_high": "RESOLVED: Temperature Back to Normal (High)",
        "recovered_low": "RESOLVED: Temperature Back to Normal (Low)",
        "daily_high": "REMINDER: High Temperature Still Active",
        "daily_low": "REMINDER: Low Temperature Still Active"
    }

    subject = SUBJECT_MAP.get(alert_type, "Temperature Alert")

    body = f"""
    <p><strong>Server Room Temperature Alert:</strong></p>

    <p>
    Temperature: {temp:.1f}°C<br>
    Humidity: {hum:.1f}%
    </p>

    <p>- Raspberry Pi Temperature Monitor</p>
    """

    SMTPClient().send(subject, body, is_html=True)