from pathlib import Path
import subprocess
import sys
import os
import signal
import time

PROJECT_ROOT = Path(__file__).resolve().parent
PITHERM_SCRIPT = PROJECT_ROOT / "PiTherm.py"
LOG_FILE = PROJECT_ROOT / "logs" / "control.log"
PID_FILE = PROJECT_ROOT / "data" / "pitherm.pid"

if os.name == "nt":
    VENV_PYTHON = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"
else:
    VENV_PYTHON = PROJECT_ROOT / "venv" / "bin" / "python"

def start():
    existing_pid = get_existing_pid()

    if existing_pid is not None:
        if is_process_running(existing_pid):
            if is_pitherm_process(existing_pid):
                print(
                    f"PiTherm is already running "
                    f"with PID {existing_pid}."
                )
                return

            print(
                f"PID {existing_pid} belongs to another process. "
                "Removing stale PID file."
            )

    remove_pid_file()

    if not VENV_PYTHON.exists():
        print(f"Python interpreter not found: {VENV_PYTHON}")
        sys.exit(1)

    if not PITHERM_SCRIPT.exists():
        print(f"PiTherm.py not found: {PITHERM_SCRIPT}")
        sys.exit(1)

    LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    log_handle = LOG_FILE.open(
        "a",
        encoding="utf-8"
    )

    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW
    else:
        creationflags = 0

    process = subprocess.Popen(
        [
            str(VENV_PYTHON),
            str(PITHERM_SCRIPT),
        ],
        cwd=PROJECT_ROOT,
        stdin=subprocess.DEVNULL,
        stdout=log_handle,
        stderr=log_handle,
        start_new_session=(os.name != "nt"),
        creationflags=creationflags,
    )

    PID_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    PID_FILE.write_text(
        str(process.pid),
        encoding="utf-8"
    )

    print(f"PiTherm started with PID {process.pid}.")

def get_existing_pid():
    if not PID_FILE.exists():
        return None

    try:
        return int(
            PID_FILE.read_text(
                encoding="utf-8"
            ).strip()
        )
    except (ValueError, OSError):
        return None

def is_process_running(pid):
    if os.name == "nt":
        try:
            output = subprocess.run(
                [
                    "tasklist",
                    "/FI",
                    f"PID eq {pid}"
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            return str(pid) in output.stdout

        except OSError:
            return False

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True

    return True

def is_pitherm_process(pid):
    if os.name == "nt":
        powershell = (
            Path(os.environ["SystemRoot"])
            / "System32"
            / "WindowsPowerShell"
            / "v1.0"
            / "powershell.exe"
        )

        result = subprocess.run (
            [
                str(powershell),
                "-NoProfile",
                "-Command",
                (
                    f"(Get-CimInstance Win32_Process "
                    f"-Filter \"ProcessId = {pid}\").CommandLine"
                ),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        command_line = result.stdout.strip()

    else:
        cmdline_path = Path(f"/proc/{pid}/cmdline")

        try:
            command_line = (
                cmdline_path
                .read_bytes()
                .replace(b"\x00", b" ")
                .decode(errors="replace")
            )

        except (FileNotFoundError, PermissionError, OSError):
            return False

    return str(PITHERM_SCRIPT).lower() in command_line.lower()

def remove_pid_file():
    PID_FILE.unlink(missing_ok=True)

def stop():
    pid = get_existing_pid()

    if pid is None:
        print("PiTherm is not running.")
        remove_pid_file()
        return True

    if not is_process_running(pid):
        print("PiTherm process is no longer running.")
        remove_pid_file()
        return True

    if not is_pitherm_process(pid):
        print(
            f"PID {pid} does not belong to PiTherm. "
            "Removing stale PID file."
        )
        remove_pid_file()
        return True

    print(f"Stopping PiTherm PID {pid}...")

    if os.name == "nt":
        result = subprocess.run(
            [
                "taskkill",
                "/F",
                "/PID",
                str(pid),
            ],
            check=False,
        )

        if result.returncode != 0:
            print(f"Failed to stop PiTherm PID {pid}.")
            return False

    else:
        os.kill(
            pid,
            signal.SIGTERM
        )

    for _ in range(50):
        if not is_process_running(pid):
            remove_pid_file()
            print("PiTherm stopped.")
            return True

        time.sleep(0.1)

    print(
        f"PiTherm PID {pid} did not stop "
        "within 5 seconds."
    )
    return False

def status():
    pid = get_existing_pid()

    if pid is None:
        print("PiTherm is not running.")
        return

    if not is_process_running(pid):
        print(
            f"PiTherm is not running. "
            f"Removing stale PID {pid}."
        )
        remove_pid_file()
        return

    if not is_pitherm_process(pid):
        print(
            f"PID {pid} belongs to another process. "
            "Removing stale PID file."
        )
        remove_pid_file()
        return

    print(f"PiTherm is running with PID {pid}.")

def restart():
    old_pid = get_existing_pid()

    print("Restarting PiTherm..")

    if not stop():
        print("Restart aborted because PiTherm could not be stopped.")
        return

    start()

    new_pid = get_existing_pid()

    print(
        f"PiTherm restarted. "
        f"Old PID: {old_pid} | New PID: {new_pid}"
    )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python control.py [start|stop|status|restart]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "start":
        start()

    elif command == "stop":
        stop()

    elif command == "status":
        status()

    elif command == "restart":
        restart()

    else:
        print(f"Unknown command: {command}")
