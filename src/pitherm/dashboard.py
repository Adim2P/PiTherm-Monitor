import requests
from src.pitherm.config import (
    ADAFRUIT_IO_USERNAME,
    ADAFRUIT_IO_KEY
)

def send_to_adafruit(temp, hum):
    if not ADAFRUIT_IO_KEY or not ADAFRUIT_IO_USERNAME:
        print("[WARN] Adafruit IO not configured. Upload skipped.")
        return

    try:
        headers = {
            "X-AIO-Key": ADAFRUIT_IO_KEY,
            "Content-Type": "application/json"
        }

        temp_url = f"https://io.adafruit.com/api/v2/{ADAFRUIT_IO_USERNAME}/feeds/temperature/data"
        hum_url = f"https://io.adafruit.com/api/v2/{ADAFRUIT_IO_USERNAME}/feeds/humidity/data"

        temp_res = requests.post(temp_url, headers=headers, json={"value": temp}, timeout=5)
        hum_res = requests.post(hum_url, headers=headers, json={"value": hum}, timeout=5)

        if temp_res.status_code == 200 and hum_res.status_code == 200:
            print("[UPLOAD] Data sent to Adafruit IO.")
        else:
            print(f"[WARN] Adafruit error: {temp_res.text} | {hum_res.text}")

    except Exception as err:
        print("[ERROR] Adafruit exception:", err)