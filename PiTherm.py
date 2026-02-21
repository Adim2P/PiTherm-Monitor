"""
===========================================================
PiTherm Monitor – Internal TODO Roadmap
===========================================================

-- PRIORITY: Safe To Implement Now (No Refactor Debt) --

[ ] Implement unified setup installer (setup.py)
    - Auto-detect OS (Windows vs Linux)
    - Create virtual environment (venv)
    - Install correct requirements file:
        * requirements-dev.txt (Windows)
        * requirements-pi.txt (Linux)
    - Upgrade pip inside venv before installing packages
    - Validate required environment variables before install completes

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

[ ] Add install / uninstall CLI argument handling
    - python setup.py install
    - python setup.py uninstall
    - Validate argument input
    - Provide clear console output for each stage

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

------------------------------------------------------------

-- POST SMS & EMAIL API MIGRATION (Avoid Refactor Debt Now) --

[ ] Rebuild SMS integration (new provider API)
    - Replace legacy SMTP-based alert flow
    - Implement new notification client module
    - Add retry logic with backoff
    - Validate API credentials at startup

[ ] Refactor temperature alerts to new notification API
    - High temperature alert
    - Low temperature alert
    - Prevent duplicate alert spam
    - Reset alert state on recovery

[ ] Implement sensor failure detection
    - Track consecutive failed reads
    - Define MAX_SENSOR_FAILURE threshold
    - Trigger hardware failure alert via new API
    - Send alert only once per failure event
    - Reset failure counter after successful sensor read

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
"""

from src.pitherm.hardware import HardwareController
from src.pitherm.monitor import Monitor
from src.pitherm.logging_service import start_scheduler

def main():
    hardware = HardwareController()
    monitor = Monitor(hardware)

    start_scheduler()
    monitor.run()

if __name__ == "__main__":
    main()