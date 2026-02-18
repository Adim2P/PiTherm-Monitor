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