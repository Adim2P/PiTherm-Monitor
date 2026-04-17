import os
import sys
from dotenv import load_dotenv

# ENVs

load_dotenv()

ADAFRUIT_IO_USERNAME = os.getenv("ADAFRUIT_IO_USERNAME")
ADAFRUIT_IO_KEY = os.getenv("ADAFRUIT_IO_KEY")
SMTP_RECIPIENT = os.getenv("SMTP_RECIPIENT")
SMTP_CC = os.getenv("SMTP_CC")
SMTP_FROM = os.getenv("SMTP_FROM")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


# Global Variables

TEMP_THRESHOLD_HIGH = 25.0
TEMP_THRESHOLD_LOW = 19.0
READ_INTERVAL_SECONDS = 30
LOG_INTERVAL_SECONDS = 300
TEMP_HYSTERESIS = 1.0

# Required ENV Variables

REQUIRED_ENV_VARS = [
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_FROM",
    "SMTP_RECIPIENT",
    "ADAFRUIT_IO_USERNAME",
    "ADAFRUIT_IO_KEY",
    "SMTP_USERNAME",
    "SMTP_PASSWORD"
]

def validate_env():
    missing = []

    for var in REQUIRED_ENV_VARS:
        value = os.getenv(var)
        if value is None or value.strip() == "":
            missing.append(var)
    
    if missing:
        print("[ERROR] Missing required environment variables:")
        for var in missing:
            print(f" - {var}")
        
        print("\n[HINT] Edit your .env file and fill in the missing values.")
        print("[HINT] Then run: python PiTherm.py")
        sys.exit(1)

    global SMTP_PORT

    try:
        SMTP_PORT = int(os.getenv("SMTP_PORT"))
    except ValueError:
        print("[ERROR] SMTP_PORT must be a valid number.")
        sys.exit(1)