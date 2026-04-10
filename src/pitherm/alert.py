from src.pitherm.smtp_client import SMTPClient

def send_email_alert(temp, hum, alert_type="high"):
    subject = "ALERT: High Temperature" if alert_type == "high" else "ALERT: Low temperature"

    body = f"""
    <p><strong>Server Room Temperature Alert:</strong></p>

    <p>
    Temperature: {temp:.1f}°C<br>
    Humidity: {hum:.1f}%
    </p>

    <p>- Raspberry Pi Temperature Monitor</p>
    """

    SMTPClient().send(subject, body, is_html=True)