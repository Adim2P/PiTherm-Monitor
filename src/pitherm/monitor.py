import time
from src.pitherm.config import (
    TEMP_THRESHOLD_HIGH,
    TEMP_THRESHOLD_LOW,
    LOG_INTERVAL_SECONDS,
    READ_INTERVAL_SECONDS,
    TEMP_HYSTERESIS
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
        
        high_reset = TEMP_THRESHOLD_HIGH - TEMP_HYSTERESIS
        low_reset = TEMP_THRESHOLD_LOW + TEMP_HYSTERESIS
        
        print(f"[DATA] Temp: {temperature:.1f}°C | Humidity: {humidity:.1f}%")

        self.hardware.update_lcd(temperature, humidity)
        current_time = time.time()
        
        if current_time - self._last_log_time >= LOG_INTERVAL_SECONDS:
            log_to_excel(temperature, humidity)
            self._last_log_time = current_time

        send_to_thingspeak(temperature, humidity)

        if temperature >= TEMP_THRESHOLD_HIGH:
            if not self.alert_sent_high:
                print("[ALERT] High Temperature threshold reached.")
                send_email_alert(temperature, humidity, alert_type="high")
                self.alert_sent_high = True

        elif self.alert_sent_high and temperature <= high_reset:
            print("[INFO] High temperature recovered.")
            self.alert_sent_high = False

        if temperature <= TEMP_THRESHOLD_LOW:
            if not self.alert_sent_low:
                print("[ALERT] Low temperature threshold reached.")
                send_email_alert(temperature, humidity, alert_type="low")
                self.alert_sent_low = True
        
        elif self.alert_sent_low and temperature >= low_reset:
            print("[INFO] Low temperature recovered.")
            self.alert_sent_low = False

        self.hardware.set_led(self.alert_sent_high or self.alert_sent_low)

    def run(self):
        print("[START] Monitoring Started. Press Ctrl + C to stop.")

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