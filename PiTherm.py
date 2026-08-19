"""
TODO: Priority to Implement

[ ] Implement SSH-safe manual start
    - Create a control.py start command
    - Launch PiTherm as a detached background process
    - Use the project virtual environment Python binary
    - Redirect stdout and stderr to log files
    - Ensure PiTherm continues running after SSH logout
    - Store the running process PID
    - Prevent duplicate PiTherm instances
    - Confirm that the process started successfully

[ ] Implement manual stop and status commands
    - Add control.py stop
    - Read the stored PID
    - Verify that the PID belongs to PiTherm
    - Send SIGTERM for graceful shutdown
    - Wait for the process to exit
    - Remove stale PID files
    - Add control.py status
    - Show whether PiTherm is running
    - Show PID and last known runtime state

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