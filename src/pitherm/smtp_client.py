import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.pitherm.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_CC,
    SMTP_RECIPIENT,
    SMTP_FROM,
    SMTP_USERNAME,
    SMTP_PASSWORD
)


def build_recipients(primary):
    cc_list = [e.strip() for e in SMTP_CC.split(",")] if SMTP_CC else []
    unique_recipients = list(set([primary] + cc_list))
    cc_list = [e for e in cc_list if e != primary]
    return primary, cc_list, unique_recipients

class SMTPClient:
    def __init__(self):
        self.host = SMTP_HOST
        self.port = int(SMTP_PORT)
        self.username = SMTP_USERNAME
        self.password = SMTP_PASSWORD
    
    def _connect(self):
        server = smtplib.SMTP(self.host, self.port, timeout=10)
        server.set_debuglevel(1) #Temporary
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(self.username, self.password)
        return server
    
    def send(self, subject, body, is_html=False, attachment=None):
        primary_to, cc_list, recipients = build_recipients(SMTP_RECIPIENT)

        msg = MIMEMultipart()
        msg["From"] = SMTP_FROM
        msg["To"] = primary_to
        msg["Subject"] = subject
        
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)

        msg.attach(MIMEText(body, "html" if is_html else "plain"))

        if attachment:
            msg.attach(attachment)
        
        try:
            server = self._connect()
            server.sendmail(SMTP_FROM, recipients, msg.as_string())
            server.quit()
            print("[OK] Email sent via SMTPClient.")
            return True
        
        except Exception as e:
            print("[ERROR] SMTPClient failed:", e)
            return False