"""
===========================================================
PiTherm Monitor – Internal TODO Roadmap
===========================================================

[ ] Implement hysteresis (anti-flapping thresholds)
    - High trigger (e.g. 25°C)
    - Reset only below buffer (e.g. 24°C)

[ ] Rebuild SMS integration (new provider API)
    - Replace legacy SMS logic
    - Add heartbeat SMS support

[ ] Create structured logging directories:
        /logs/
            /current/
            /archive/

[ ] Save active month logs in /logs/current

[ ] Automatically archive previous month to /logs/archive

[ ] Ensure file operations are thread-safe

[ ] Implement fallback logging (CSV or text)
    - Trigger if Excel write fails
    - Prevent data loss

[ ] Sensor failure detection
    - Track consecutive failed reads
    - Alert if threshold exceeded

[ ] Watchdog timer
    - Detect stalled loop
    - Trigger recovery or alert

[ ] Heartbeat monitoring
    - Daily health report
    - Include uptime and last reading
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