import requests
from src.pitherm.config import THINGSPEAK_API_KEY

def send_to_thingspeak(temp, hum):
    url = "https://api.thingspeak.com/update"
    params = {
        'api_key': THINGSPEAK_API_KEY,
        'field1': temp,
        'field2': hum,
    }

    if not THINGSPEAK_API_KEY:
        print ("[WARN] ThingSpeak API key not configured. Upload skipped.")
        return

    try:
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200 and r.text !='0':
            print("[UPLOAD] Data sent to ThingSpeak.")
        else:
            print(f"[WARN] ThingSpeak error: {r.text}")
    except Exception as err:
        print("[ERROR] ThingSpeak exception:", err)