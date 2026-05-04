from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.pitherm import config
import smtplib

def build_recipients(primary):
    cc_list = [e.strip() for e in config.SMTP_CC.split(",")] if config.SMTP_CC else []
    cc_list = [e for e in cc_list if e and e != primary]

    recipients = []
    for email in [primary] + cc_list:
        if email not in recipients:
            recipients.append(email)

    return primary, cc_list, recipients

class SMTPClient:
    def _connect(self, host, port):
        server = smtplib.SMTP(host, port, timeout=10)
        server.starttls()
        return server
    
    def send(self, subject, body, is_html=False, attachment=None):
        if not config.EMAIL_ENABLED:
            print("[TEST MODE] Email skipped.")
            print(f"[TEST EMAIL] Subject: {subject}")
            return True
        
        if not config.is_smtp_configured():
            print("[WARN] SMTP not configured. Email skipped.")
            return False

        smtp_host = config.SMTP_HOST
        smtp_port = config.SMTP_PORT
        smtp_from = config.SMTP_FROM
        smtp_recipient = config.SMTP_RECIPIENT

        if (
            smtp_host is None or
            smtp_port is None or
            smtp_from is None or
            smtp_recipient is None
        ):
            print("[WARN] SMTP not configured. Email skipped.")
            return False

        primary_to, cc_list, recipients = build_recipients(smtp_recipient)

        msg = MIMEMultipart()
        msg["From"] = smtp_from
        msg["To"] = primary_to

        if cc_list:
            msg["Cc"] = ", ".join(cc_list)
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html" if is_html else "plain"))

        if attachment:
            msg.attach(attachment)
        
        try:
            server = self._connect(smtp_host, int(smtp_port))
            server.sendmail(smtp_from, recipients, msg.as_string())
            server.quit()
            print(f"[OK] Email sent via SMTPClient. Subject: {subject}")
            return True
        
        except Exception as e:
            print("[ERROR] SMTPClient failed:", e)
            return False
