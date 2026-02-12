import os
from dotenv import load_dotenv

# ENVs

load_dotenv()

THINGSPEAK_API_KEY = os.getenv("THINGSPEAK_API_KEY")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_RECIPIENT = os.getenv("SMTP_RECIPIENT")
SMTP_CC = os.getenv("SMTP_CC")

# Global Variables

TEMP_THRESHOLD_HIGH = 25.0
TEMP_THRESHOLD_LOW = 19.0
