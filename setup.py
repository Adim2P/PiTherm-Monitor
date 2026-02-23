import os
import sys
import platform
import subprocess
import shutil

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
VENV_PATH = os.path.join(PROJECT_ROOT, "venv")
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
SERVICE_FILE_PATH = "/etc/systemd/system/pitherm.service"

REQUIRED_ENV_KEYS = ["THINGSPEAK_API_KEY"]

def run_command(command, check=True):
    result = subprocess.run(command, shell=True)
    if check and result.returncode != 0:
        print(f"[ERROR] Command failed: {command}")
        sys.exit(1)

def create_venv():
    if os.path.exists(VENV_PATH):
        print("[INFO] Virtual environment already exists.")
        return
    
    print("[STEP] Creating virtual environment...")
    run_command(f"python3 -m venv {VENV_PATH}")

def upgrade_pip():
    print("[STEP] Upgrading pip inside venv...")
    pip_path = os.path.join(VENV_PATH, "bin", "pip")
    run_command(f"{pip_path} install --upgrade pip")

def install_requirements():
    system = platform.system()

    if system == "Linux":
        req_file = "requirements-pi.txt"
    elif system == "Windows":
        req_file = "requirements-dev.txt"
    else:
        print("[ERROR] Unsupported OS.")
        sys.exit(1)
    
    print(f"[STEP] Installing dependencies from {req_file}...")
    pip_path = os.path.join(VENV_PATH, "bin", "pip")
    run_command(f"{pip_path} install -r {req_file}")

def create_env_file():
    if os.path.exists(ENV_FILE):
        print("[INFO] .env file already exists.")
        return

    print("[STEP] Creating .env file...")
    with open(ENV_FILE, "w") as f:
        f.write("THINGSPEAK_API_KEY=\n")
        f.write("SMTP_USER=\n")
        f.write("SMTP_PASS=\n")
        f.write("SMTP_RECIPIENT=\n")
        f.write("SMTP_CC=\n")

def validate_env():
    print("[STEP] Validating required environment variables...")

    values = {}
    with open(ENV_FILE, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                values[key] = value.strip()

    for key in REQUIRED_ENV_KEYS:
        if not values.get(key):
            print(f"[WARNING] Required key '{key}' is not set.")
            return False
        
    return True