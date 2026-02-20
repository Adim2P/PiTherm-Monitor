"""
===========================================================
PiTherm Monitor – Internal TODO Roadmap
===========================================================

[ ] Rebuild SMS integration (new provider API)
    - Replace legacy SMS logic
    - Add heartbeat SMS support

[ ] Sensor failure detection
    - Track consecutive failed reads
    - Alert if threshold exceeded

[ ] Watchdog timer
    - Detect stalled loop
    - Trigger recovery or alert

[ ] Heartbeat monitoring
    - Daily health report
    - Include uptime and last reading

[ ] Implement unified setup installer (setup.py)
    - Auto-detect OS (Windows vs Linux)
    - Create virtual environment (venv)
    - Install correct requirements file:
        * requirements-dev.txt (Windows)
        * requirements-pi.txt (Linux)
    - Upgrade pip inside venv before installing packages

[ ] Implement automatic systemd service registration (Linux only)
    - Dynamically generate pitherm.service
    - Set WorkingDirectory to project root
    - Use venv Python binary in ExecStart
    - Enable service on boot
    - Start service immediately after install
    - Configure Restart=always and RestartSec=5

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

[ ] (Optional – Future Hardening)
    - Add --status flag (check service status)
    - Add version stamping in systemd description
    - Add logging of installer actions
    - Validate user permissions before install

[ ] Integrate fallback failure alerting (Post API Migration)
    - Trigger alert when Excel logging fails
    - Hook alert into new SMS / notification API (not SMTP)
    - Ensure alert sends only once per failure event
    - Prevent alert spam during repeated failures
    - Reset failure state when Excel logging recovers

[ ] Implement logging failure state tracking
    - Add boolean flag: excel_faulted
    - Set to True when fallback is triggered
    - Reset to False after successful Excel write
    - Expose state for heartbeat reporting

[ ] Include logging health in future heartbeat report
    - Report NORMAL or FALLBACK_ACTIVE
    - Include last successful Excel write timestamp
    - Ensure visibility in daily system health report
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