import os
from datetime import datetime, timedelta
import src.pitherm.logging_service as test

CURRENT_DIR = test.CURRENT_DIR
ARCHIVE_DIR = test.ARCHIVE_DIR

os.makedirs(CURRENT_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

print("[INFO] CURRENT_DIR:", CURRENT_DIR)
print("[INFO] ARCHIVE_DIR:", ARCHIVE_DIR)

def get_week_str(dt):
    year, week, _ = dt.isocalendar()
    return f"{year}_W{week:02d}"

now = datetime.now()

current_week_str = get_week_str(now)
old_week_str = get_week_str(now - timedelta(days=7))

current_file = f"temp_log_{current_week_str}.xlsx"
old_file = f"temp_log_{old_week_str}.xlsx"

current_path = os.path.join(CURRENT_DIR, current_file)
old_path = os.path.join(CURRENT_DIR, old_file)

open(current_path, "w").close()
open(old_path, "w").close()

print("\n[SETUP] Created files:")
print(" -", current_file, "(should STAY)")
print(" -", old_file, "(should ARCHIVE)")


print("\n[RUN] Running archive_logs()...")
test.archive_old_logs()

print("\n[RESULT]")
print("\nCURRENT_DIR contents:")

for f in os.listdir(CURRENT_DIR):
    print(" -", f)

print("\nARCHIVE_DIR contents:")
for f in os.listdir(ARCHIVE_DIR):
    print(" -", f)

"""
print("\n[CLEANUP] Removing test files...")

for path in [current_path, os.path.join(ARCHIVE_DIR, old_file)]:
    if os.path.exists(path):
        os.remove(path)

print("[DONE]")
"""