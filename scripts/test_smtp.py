from src.pitherm.smtp_client import SMTPClient

client = SMTPClient()

subject = "PiTherm SMTP Test"
body = "If you see this, SMTP is working."

print("[INFO] Sending Email now")
client.send(subject, body)