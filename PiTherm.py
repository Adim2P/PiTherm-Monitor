"""
TODO: Priority to Implement

[ ] Implement automatic systemd service registration (Linux only)
    - Dynamically generate pitherm.service
    - Set WorkingDirectory to project root
    - Use venv Python binary in ExecStart
    - Enable service on boot
    - Start service immediately after install
    - Configure Restart=always and RestartSec=5
    - Validate service status after registration

[ ] Implement clean uninstall capability
    - Stop running service
    - Disable service from startup
    - Remove /etc/systemd/system/pitherm.service
    - Reload systemd daemon
    - Remove virtual environment (venv)
    - Ensure no leftover files or processes remain

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

[ ] Heartbeat monitoring (Structure Only – No API Integration Yet)
    - Track system uptime
    - Track last sensor reading timestamp
    - Track hardware_ready state
    - Track excel_faulted state
    - Prepare structured health report payload (no sending yet)

[ ] Watchdog timer
    - Detect stalled main monitoring loop
    - Track last successful loop execution timestamp
    - Log watchdog trigger event
    - Prepare hook for future notification integration

[ ] Integrate fallback failure alerting
    - Trigger alert when Excel logging fails
    - Hook alert into new notification API
    - Ensure alert sends only once per failure event
    - Prevent alert spam during repeated failures
    - Reset failure state when Excel logging recovers

[ ] Enable full heartbeat notification delivery
    - Send daily health report via new API
    - Include uptime, hardware_ready, excel_faulted
    - Include last successful Excel write timestamp
    - Include last sensor reading timestamp

TODO: Some changes as per request, and bug fixes
! IMPORTANT: To be fixed right away

- Daily sending of Email, if Temps are still well above High Threshold
- Add an email sending feature when temps reach normal level 
  after high temperature or low temperature
-  Add one more decimal point
- Logging Catch for any Hardware Hiccups

? Edge Cases:

- Since Alarm states are permanent, what if it's not resolved
  during non work hours? Should there still be sending of email
  alert after some time?

"""
import sys
import os

def is_venv():
    return sys.prefix != sys.base_prefix

if not is_venv():
    print("[ERROR] Not running inside a virtual environment.")
    
    if not os.path.exists("venv"):
        print("[HINT] Project is not set up yet.")
        print("Run: python setup.py install")
    else:
        print("[HINT] Activate your venv first:")
        if os.name == "nt":
            print(" venv\\Scripts\\activate")
        else:
            print(" source venv/bin/activate")

    print("\nThen Run: python PiTherm.py")
    exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("[ERROR] Required dependencies not installed.")
    print("Run: python setup.py install")
    exit(1)

from src.pitherm.hardware import HardwareController
from src.pitherm.monitor import Monitor
from src.pitherm.logging_service import start_scheduler
from src.pitherm.config import validate_env

validate_env()

def main():
    print(f"[START] Using python: {sys.executable}")

    hardware = HardwareController()
    monitor = Monitor(hardware)

    start_scheduler()
    monitor.run()

if __name__ == "__main__":
    main()