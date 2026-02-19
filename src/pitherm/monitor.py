import time
from src.pitherm.config import (
    TEMP_THRESHOLD_HIGH,
    TEMP_THRESHOLD_LOW,
    LOG_INTERVAL_SECONDS,
    READ_INTERVAL_SECONDS
)
from src.pitherm.alert import (
    send_email_alert
)
from src.pitherm.logging_service import log_to_excel
from src.pitherm.dashboard import send_to_thingspeak

class Monitor:
    def __init__(self, hardware):
        self.hardware = hardware
        self.alert_sent_high = False
        self.alert_sent_low = False
        self._last_log_time = 0
    
    def process_reading(self, temperature, humidity):
        print(f"[DATA] Temp: {temperature:.1f}°C | Humidity: {humidity:.1f}%")

        self.hardware.update_lcd(temperature, humidity)

        current_time = time.time()
        
        if current_time - self._last_log_time >= LOG_INTERVAL_SECONDS:
            log_to_excel(temperature, humidity)
            self._last_log_time = current_time

        send_to_thingspeak(temperature, humidity)

        if temperature >= TEMP_THRESHOLD_HIGH:
            print("[DEBUG] High temp alert triggered!")
            self.hardware.set_led(True)

            if not self.alert_sent_high:
                send_email_alert(temperature, humidity, alert_type="high")

                self.alert_sent_high = True
                self.alert_sent_low = False
        elif temperature <= TEMP_THRESHOLD_LOW:
            print("[DEBUG] Low temp alert triggered!")
            self.hardware.set_lcd(True)

            if not self.alert_sent_low:
                send_email_alert(temperature, humidity, alert_type="low")

                self.alert_send_low = True
                self.alert_send_high = False
        else:
            self.hardware.set_led(False)
            self.alert_sent_high = False
            self.alert_send_low = False
    
    def run(self):
        print ("[START] Monitoring Started. Press Ctrl + C to stop.")

        try:
            while True:
                try:
                    temperature, humidity = self.hardware.read_sensor()

                    if temperature is not None and humidity is not None:
                        try:
                            self.process_reading(temperature, humidity)
                        except Exception as e:
                            print("[ERROR] Processing failure:", e)
                    else:
                        print("[WARN] Sensor read failed.")
                
                except RuntimeError as err:
                    print(f"[ERROR] DHT read error: {err}")
                
                time.sleep(READ_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\n[STOP] Monitoring stopped by user.")

        finally:
            self.hardware.cleanup()