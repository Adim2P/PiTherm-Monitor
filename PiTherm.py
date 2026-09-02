"""
TODO: Priority to Implement

[ ] BUG: Runtime.log still duplicates, would implement daily runtime
    log instead, archiving previous daily runtime for new one.

[ ] Feature: Implement Preferred Excel Formatting (Auto Width, Border, 
    and Bold Columns)

[ ] Feature: Add persistent state tracking for weekly Excel reports and daily alerts.
    If SMTP is unavailable or times out, record which reports/alerts failed to send. 
    Once SMTP connectivity is restored, automatically send all missed items along with 
    the current scheduled report.
    Example: If weekly reports for Weeks 35 and 36 fail, the Week 37 Monday email should 
    include Weeks 35, 36, and 37.

[ ] BUG: If previous excel week has failed, it would try to send the
    previous week's file for the week it should be supposed to send.
    (e.g. if 35th Week has failed, it would try to send it in 36th,
    if SMTP has failed. Connnected with issue above.)

[ ] Validate PiTherm startup from control.py
    - Wait briefly after launching PiTherm
    - Confirm the child PID is still running
    - Confirm the PID belongs to PiTherm.py
    - Remove the PID file if startup fails
    - Report startup failure instead of reporting success
    - Direct user to control.log for startup errors

[ ] Implement PiTherm watchdog and automatic recovery
    - Add a lightweight health/heartbeat state for the monitoring worker
    - Record the timestamp of the last successfully completed monitoring cycle
    - Record the timestamp of the last successful Adafruit upload separately
    - Keep watchdog health data separate from runtime_state.json
    - Detect when the monitoring loop has stopped updating for too long
    - Distinguish a frozen worker from a temporary Adafruit/network failure
    - Restart PiTherm automatically when the worker heartbeat becomes stale
    - Use the existing control/start/stop logic for recovery where possible
    - Wait for a successful heartbeat after restart before marking recovery complete
    - Log watchdog-triggered restarts and the reason for recovery
    - Add restart backoff to prevent rapid restart loops
    - Stop automatic recovery after repeated failures within a short period
    - Send an SMTP notification when automatic recovery succeeds
    - Send a critical SMTP notification when repeated recovery attempts fail

[ ] Implement scheduled weekly restart
    - Restart PiTherm automatically every Saturday
    - Make the restart time configurable
    - Ensure the scheduled restart only happens once per Saturday
    - Perform a graceful stop before starting the worker again
    - Preserve runtime_state.json across the restart
    - Confirm the new worker is healthy before reporting success
    - Send an SMTP notification after a successful scheduled restart

[ ] Refactor runtime logging to daily log rotation
    - Replace size-based RotatingFileHandler with TimedRotatingFileHandler
    - Keep runtime.log as the active log file for the current day
    - Rotate runtime.log automatically at midnight
    - Rename rotated logs using the previous day's date
    - Use a clear date-based filename format such as runtime_YYYY-MM-DD.log
    - Keep daily logs separate to make error investigation easier
    - Configure how many historical daily logs should be retained
    - Ensure logging continues cleanly after midnight rotation
    - Verify rotation behavior on both Windows and Raspberry Pi/Linux
    - Confirm existing runtime.log data is preserved during migration

[ ] Implement Dashboard after Persistent Flag States using local
    native UI

"""

import sys
import os
from src.pitherm.logger import logger

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_PATH = os.path.join(PROJECT_ROOT, "venv")

def is_venv():
    return sys.prefix != sys.base_prefix

if not is_venv():
    logger.error("Not running inside a virtual environment.")
    
    if not os.path.exists(VENV_PATH):
        logger.info("[HINT] Project is not set up yet.")
        logger.info("Run: python setup.py install")
    else:
        logger.info("[HINT] Activate your venv first:")
        if os.name == "nt":
            logger.info(" venv\\Scripts\\activate")
        else:
            logger.info(" source venv/bin/activate")

    logger.info("\nThen Run: python PiTherm.py")
    exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    logger.error("Required dependencies not installed.")
    logger.info("Run: python setup.py install")
    exit(1)

from src.pitherm.hardware import HardwareController
from src.pitherm.monitor import Monitor
from src.pitherm.logging_service import start_scheduler
from src.pitherm.config import validate_env, print_config
import signal

validate_env()
print_config()

def main():
    logger.info(f"[START] Using python: {sys.executable}")

    hardware = HardwareController()
    monitor = Monitor(hardware)

    def handle_shutdown(signum, frame):
        monitor.stop()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    start_scheduler()
    monitor.run()

if __name__ == "__main__":
    main()