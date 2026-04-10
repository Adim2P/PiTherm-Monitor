# Script for Testing Excel Attachment for Email Sending

from src.pitherm.logging_service import send_monthly_report

print("[DEBUG] Initiating Script")

def debug():
    print("[DEBUG] Sending Excel Email Attachment.")
    try:
        send_monthly_report()
    except Exception as e:
        print("[DEBUG] Email Sending Failed:", e)

if __name__ == "__main__":
    debug()