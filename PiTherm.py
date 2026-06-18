"""
TODO: Priority to Implement

[ ] Implementation of Phase 2 for State Manager on Week Report
    Tracking

[ ] Adding a Tolerance feature, that doesn't consider very big
    or low temp differences from the normal, reading.

[ ] Implement automatic systemd service registration (Linux only)
    - Dynamically generate pitherm.service
    - Set WorkingDirectory to project root
    - Use venv Python binary in ExecStart
    - Enable service on boot
    - Start service immediately after install
    - Configure Restart=always and RestartSec=5
    - Validate service status after registration

[ ] Implement CI/CD Pipeline

[ ] Implement clean uninstall capability
    - Stop running service
    - Disable service from startup
    - Remove /etc/systemd/system/pitherm.service
    - Reload systemd daemon
    - Remove virtual environment (venv)
    - Ensure no leftover files or processes remain

[ ] Implement Dashboard after Persistent Flag States using local
    native UI

------------------------------------------------------------

TODO: When main installer Implementation is done

[ ] Implement sensor failure detection
    - Track consecutive failed reads
    - Define MAX_SENSOR_FAILURE threshold
    - Trigger hardware failure alert via new API
    - Send alert only once per failure event
    - Reset failure counter after successful sensor read

[ ] Improve DHT hardware self-test robustness
    - Retry initial sensor read 2–3 times before failing
    - Add small delay between retries
    - Log retry attempts during initialization
    - Only enter dev mode if all retries fail

[ ] Improve LCD initialization validation
    - Detect I2C initialization failure explicitly
    - Attempt simple test write during startup
    - Log clear diagnostic message if LCD fails
    - Consider fallback mode if only LCD fails but DHT works

[ ] Implement logging failure state tracking
    - Add boolean flag: excel_faulted
    - Set to True when fallback is triggered
    - Reset to False after successful Excel write
    - Track last successful Excel write timestamp
    - Expose state internally for monitoring

[ ] Integrate fallback failure alerting
    - Trigger alert when Excel logging fails
    - Hook alert into new notification API
    - Ensure alert sends only once per failure event
    - Prevent alert spam during repeated failures
    - Reset failure state when Excel logging recovers

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