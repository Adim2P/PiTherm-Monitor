import os
import sys
from dotenv import load_dotenv
import configparser
from datetime import datetime

# ENVs

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")

_config = configparser.ConfigParser()

def load_ini():
    if not os.path.exists(CONFIG_FILE):
        print("[INFO] config.ini not found. Creating default config.")

        _config["thresholds"] = {
            "temp_high": "25.0",
            "temp_low": "19.0",
            "hysteresis": "1.0"
        }

        _config["intervals"] = {
            "read_seconds": "30",
            "log_seconds": "300"
        }

        _config["alerts"] = {
            "daily_alert_time": "09:00",
            "email_enabled": "true"
        }

        with open(CONFIG_FILE, "w") as f:
            _config.write(f)
    
    else:
        _config.read(CONFIG_FILE)

load_ini()

ADAFRUIT_IO_USERNAME = os.getenv("ADAFRUIT_IO_USERNAME")
ADAFRUIT_IO_KEY = os.getenv("ADAFRUIT_IO_KEY")
SMTP_RECIPIENT = os.getenv("SMTP_RECIPIENT")
SMTP_CC = os.getenv("SMTP_CC")
SMTP_FROM = os.getenv("SMTP_FROM")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
ALLOW_FAKE_HARDWARE = os.getenv("ALLOW_FAKE_HARDWARE", "").strip().lower() in (
    "1",
    "true",
    "yes",
)

# Global Variables

TEMP_THRESHOLD_HIGH = float(_config["thresholds"]["temp_high"])
#TEMP_THRESHOLD_HIGH = 25.0
TEMP_THRESHOLD_LOW = float(_config["thresholds"]["temp_low"])
#TEMP_THRESHOLD_LOW = 19.0
READ_INTERVAL_SECONDS = int(_config["intervals"]["read_seconds"])
#READ_INTERVAL_SECONDS = 30
LOG_INTERVAL_SECONDS = int(_config["intervals"]["log_seconds"])
#LOG_INTERVAL_SECONDS = 300
TEMP_HYSTERESIS = float(_config["thresholds"]["hysteresis"])
#TEMP_HYSTERESIS = 1.0
DAILY_ALERT_TIME = _config["alerts"]["daily_alert_time"]
EMAIL_ENABLED = _config["alerts"]["email_enabled"].lower() in ("1", "true", "yes")

SMTP_REQUIRED_ENV_VARS = [
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_FROM",
    "SMTP_RECIPIENT",
]

def is_smtp_configured():
    return all(
        value is not None and value.strip() != ""
        for value in (SMTP_HOST, SMTP_PORT, SMTP_FROM, SMTP_RECIPIENT)
    )

def validate_env():
    smtp_started = False

    for var in SMTP_REQUIRED_ENV_VARS:
        value = os.getenv(var)
        if value is not None and value.strip() != "":
            smtp_started = True
            break

    if not smtp_started:
        print("[INFO] SMTP not configured. Email features disabled.")
        return

    missing = []

    for var in SMTP_REQUIRED_ENV_VARS:
        value = os.getenv(var)
        if value is None or value.strip() == "":
            missing.append(var)
    
    if missing:
        print("[ERROR] Missing required environment variables:")
        for var in missing:
            print(f" - {var}")
        
        print("\n[HINT] SMTP is optional, but partial SMTP config is not.")
        print("[HINT] Fill in SMTP_HOST, SMTP_PORT, SMTP_FROM, and SMTP_RECIPIENT, or leave all blank.")
        sys.exit(1)

    smtp_port_value = os.getenv("SMTP_PORT")

    if smtp_port_value is None:
        print("[ERROR] SMTP_PORT must be set when SMTP is configured.")
        sys.exit(1)

    try:
        int(smtp_port_value)
    except ValueError:
        print("[ERROR] SMTP_PORT must be a valid number.")
        sys.exit(1)

def print_config():
    print(f"[CONFIG] High={TEMP_THRESHOLD_HIGH}, Low={TEMP_THRESHOLD_LOW}")
    print(f"[CONFIG] Hysteresis={TEMP_HYSTERESIS}")
    print(f"[CONFIG] Daily Alert Time={DAILY_ALERT_TIME}")
    print(f"[CONFIG] Email Enabled={EMAIL_ENABLED}")
    print(f"[CONFIG] Fake Hardware Enabled={ALLOW_FAKE_HARDWARE}")
