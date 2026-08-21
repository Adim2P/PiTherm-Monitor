import os
import sys
import subprocess
import platform
import shutil
from src.pitherm.logger import logger

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(PROJECT_ROOT, "venv")
OS = platform.system()
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
ENV_EXAMPLE = os.path.join(PROJECT_ROOT, ".env.example")

def run(cmd):
    logger.info(f"[RUN] {' '.join(cmd)}")
    subprocess.check_call(cmd)

def get_pip():
    if OS == "Windows":
        return os.path.join(VENV_DIR, "Scripts", "pip")
    return os.path.join(VENV_DIR, "bin", "pip")

def get_python():
    if OS == "Windows":
        return os.path.join(VENV_DIR, "Scripts", "python")
    return os.path.join(VENV_DIR, "bin", "python")

def create_venv():
    if not os.path.exists(VENV_DIR):
        logger.info("[INFO] Creating virtual environment...")
        run([sys.executable, "-m", "venv", VENV_DIR])
    else:
        logger.info("[INFO] venv already exists.")

def install_requirements():
    req_file = "requirements-dev.txt" if OS == "Windows" else "requirements-pi.txt"
    pip = get_pip()
    python_exec = get_python()
    logger.info(f"[INFO] Installing dependencies from {req_file}")
    run([python_exec, "-m", "pip", "install", "--upgrade", "pip"])
    run([pip, "install", "-r", req_file])

def setup_env_file():
    if os.path.exists(ENV_FILE):
        logger.info("[INFO] .env already exists. Skipping.")
        return
    
    if not os.path.exists(ENV_EXAMPLE):
        logger.warning(".env.example is not found. Skipping env setup.")
        return
    
    logger.info("[INFO] Creating .env from template...")

    with open(ENV_EXAMPLE, "r") as src:
        content = src.read()
    
    with open(ENV_FILE, "w") as dst:
        dst.write(content)

    logger.info("[OK] .env file created.")
    logger.info("[HINT] Please edit .env and fill in required values.")

def install():
    create_venv()
    install_requirements()
    setup_env_file()
    logger.info("[SUCESS] Basic install complete.")


def uninstall():
    if not os.path.exists(VENV_DIR):
        logger.info("[INFO] No virtual environment found. Nothing to remove.")
        return

    logger.info("[INFO] Removing virtual environment...")
    
    try:
        shutil.rmtree(VENV_DIR)
        logger.info("[OK] venv removed.")

    except PermissionError:
        logger.error("Could not remove venv (Acess Denied).")
        logger.error("Make Sure:")
        logger.error(" - You are not inside the venv (run 'deactivate')")
        logger.error(" - No terminal or process is using it")
        logger.error(" - Close VS Code or any running Python Scipts")
    
    except Exception as e:
        logger.error(
            f"Unexpected error: {e}", 
            exc_info=True
        )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.info("Usage: python setup.py [install|uninstall]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "install":
        install()
    elif cmd == "uninstall":
        uninstall()
    else:
        logger.error("Invalid command")
