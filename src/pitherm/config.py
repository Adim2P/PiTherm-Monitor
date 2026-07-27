import os
import sys
from dotenv import load_dotenv
import configparser
from src.pitherm.logger import logger

# ENVs

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")

_config = configparser.ConfigParser()

def load_ini():
    if not os.path.exists(CONFIG_FILE):
        logger.info("[INFO] config.ini not found. Creating default config.")

        _config["thresholds"] = {
            "temp_high": "25.0",
            "temp_low": "19.0",
            "hysteresis": "1.0",
            "humidity_low": "40.0",
            "humidity_high": "60.0",
        }

        _config["intervals"] = {
            "read_seconds": "30",
            "log_seconds": "300"
        }

        _config["alerts"] = {
            "daily_alert_time": "09:00",
            "email_enabled": "true"
        }

        _config["validation"] = {
            "temp_min_valid": "0.0",
            "temp_max_valid": "60.0",
            "humidity_min_valid": "0.0",
            "humidity_max_valid": "100.0",
            "max_temp_jump": "8.0",
            "max_humidity_jump": "25.0"
        }

        with open(CONFIG_FILE, "w") as f:
            _config.write(f)
    
    else:
        _config.read(CONFIG_FILE)

load_ini()

# Global Variables

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
TEMP_THRESHOLD_HIGH = float(
    _config["thresholds"]["temp_high"]
)
TEMP_THRESHOLD_LOW = float(
    _config["thresholds"]["temp_low"]
)
HUMIDITY_THRESHOLD_LOW = float(
    _config["thresholds"]["humidity_low"]
)
HUMIDITY_THRESHOLD_HIGH = float(
    _config["thresholds"]["humidity_high"]
)
READ_INTERVAL_SECONDS = int(
    _config["intervals"]["read_seconds"]
)
LOG_INTERVAL_SECONDS = int(
    _config["intervals"]["log_seconds"]
)
TEMP_HYSTERESIS = float(
_config["thresholds"]["hysteresis"]
)
DAILY_ALERT_TIME = _config["alerts"]["daily_alert_time"]
EMAIL_ENABLED = _config["alerts"]["email_enabled"].lower() in (
    "1", 
    "true",
    "yes"
)
SMTP_REQUIRED_ENV_VARS = [
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_FROM",
    "SMTP_RECIPIENT",
]
TEMP_MIN_VALID = float(
    _config["validation"]["temp_min_valid"]
)
TEMP_MAX_VALID = float(
    _config["validation"]["temp_max_valid"]
)
HUMIDITY_MIN_VALID = float(
    _config["validation"]["humidity_min_valid"]
)
HUMIDITY_MAX_VALID = float(
    _config["validation"]["humidity_max_valid"]
)
MAX_TEMP_JUMP = float(
    _config["validation"]["max_temp_jump"]
)
MAX_HUMIDITY_JUMP = float(
    _config["validation"]["max_humidity_jump"]
)

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
        logger.info("SMTP not configured. Email features disabled.")
        return

    missing = []

    for var in SMTP_REQUIRED_ENV_VARS:
        value = os.getenv(var)
        if value is None or value.strip() == "":
            missing.append(var)
    
    if missing:
        logger.error("Missing required environment variables:")
        for var in missing:
            logger.info(f" - {var}")
        
        logger.info("\n[HINT] SMTP is optional, but partial SMTP config is not.")
        logger.info("[HINT] Fill in SMTP_HOST, SMTP_PORT, SMTP_FROM, and SMTP_RECIPIENT, or leave all blank.")
        sys.exit(1)

    smtp_port_value = os.getenv("SMTP_PORT")

    if smtp_port_value is None:
        logger.error("SMTP_PORT must be set when SMTP is configured.")
        sys.exit(1)

    try:
        int(smtp_port_value)
    except ValueError:
        logger.error("SMTP_PORT must be a valid number.")
        sys.exit(1)

def print_config():
    logger.info(
        f"[CONFIG] High= {TEMP_THRESHOLD_HIGH}, Low={TEMP_THRESHOLD_LOW}"
    )
    logger.info(
        f"[CONFIG] Humidity Optimal = "
        f"{HUMIDITY_THRESHOLD_LOW}% - {HUMIDITY_THRESHOLD_HIGH}%"
    )
    logger.info(
        f"[CONFIG] Hysteresis= {TEMP_HYSTERESIS}"
    )
    logger.info(
        f"[CONFIG] Daily Alert Time= {DAILY_ALERT_TIME}"
    )
    logger.info(
        f"[CONFIG] Email Enabled= {EMAIL_ENABLED}"
    )
    logger.info(
        f"[CONFIG] Fake Hardware Enabled= {ALLOW_FAKE_HARDWARE}"
    )
    logger.info(
        f"[CONFIG] Temp Validation= {TEMP_MIN_VALID}°C - {TEMP_MAX_VALID}°C"
    )
    logger.info(
        f"[CONFIG] Humidity Validation= {HUMIDITY_MIN_VALID}% - {HUMIDITY_MAX_VALID}%"
    )
    logger.info(
        f"[CONFIG] Max Temp Jump= {MAX_TEMP_JUMP}°C"
    )
    logger.info(
        f"[CONFIG] Max Humidity Jump= {MAX_HUMIDITY_JUMP}%"
    )
