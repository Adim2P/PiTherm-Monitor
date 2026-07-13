import time
from src.pitherm.config import (
    TEMP_THRESHOLD_HIGH,
    TEMP_THRESHOLD_LOW,
    LOG_INTERVAL_SECONDS,
    READ_INTERVAL_SECONDS,
    TEMP_HYSTERESIS
)
from src.pitherm.alert import send_email_alert
from src.pitherm.logging_service import log_to_excel
from src.pitherm.dashboard import send_to_adafruit
from datetime import datetime
from src.pitherm.config import DAILY_ALERT_TIME
from src.pitherm.logger import logger
from src.pitherm.state_manager import state
from src.pitherm.sensor_validator import SensorValidator

class Monitor:
    def __init__(self, hardware):
        self.hardware = hardware
        self.validator = SensorValidator()
        self._last_log_time = 0
        self._running = True
        self.alert_sent_high = state.get(
            "alert_sent_high",
            False
        )
        self.alert_sent_low = state.get(
            "alert_sent_low",
            False
        )
        self.last_daily_high_alert_date = state.get(
            "last_daily_high_alert_date"
        )
        self.last_daily_low_alert_date = state.get(
            "last_daily_low_alert_date"
        )

        logger.info(
            f"[STATE] Restored alert_sent_high={self.alert_sent_high}"
        )

        logger.info(
            f"[STATE] Restored alert_sent_low={self.alert_sent_low}"
        )
    
    def process_reading(self, temperature, humidity):
        
        high_reset = TEMP_THRESHOLD_HIGH - TEMP_HYSTERESIS
        low_reset = TEMP_THRESHOLD_LOW + TEMP_HYSTERESIS
        today = str(datetime.now().date())
        
        logger.info(f"[DATA] Temp: {temperature:.2f}°C | Humidity: {humidity:.2f}%")

        self.hardware.update_lcd(temperature, humidity)
        current_time = time.time()
        
        if current_time - self._last_log_time >= LOG_INTERVAL_SECONDS:
            log_to_excel(temperature, humidity)
            self._last_log_time = current_time

        send_to_adafruit(temperature, humidity)

        if temperature >= TEMP_THRESHOLD_HIGH:
            if not self.alert_sent_high:
                logger.warning("[ALERT] High Temperature threshold reached.")
                send_email_alert(temperature, humidity, alert_type="high")
                self.alert_sent_high = True
                state.set("alert_sent_high", True)
                self.last_daily_high_alert_date = today
                state.set(
                    "last_daily_high_alert_date",
                    today
                )
            
            elif self._is_time_for_daily_alert():
                if self.last_daily_high_alert_date != today:
                    logger.warning("[DAILY ALERT] High temperature still active.")
                    send_email_alert(temperature, humidity, alert_type="daily_high")
                    self.last_daily_high_alert_date = today
                    state.set(
                        "last_daily_high_alert_date", 
                        today
                    )

        elif self.alert_sent_high and temperature <= high_reset:
            logger.info("High temperature recovered.")
            send_email_alert(temperature, humidity, alert_type="recovered_high")
            self.alert_sent_high = False
            state.set("alert_sent_high", False)

        if temperature <= TEMP_THRESHOLD_LOW:
            if not self.alert_sent_low:
                logger.warning("[ALERT] Low temperature threshold reached.")
                send_email_alert(temperature, humidity, alert_type="low")
                self.alert_sent_low = True
                state.set("alert_sent_low", True)
                self.last_daily_low_alert_date = today
                state.set(
                    "last_daily_low_alert_date", 
                    today
                )

            elif self._is_time_for_daily_alert():
                if self.last_daily_low_alert_date != today:
                    logger.warning("[DAILY ALERT] Low temperature still active.")
                    send_email_alert(temperature, humidity, alert_type="daily_low")
                    self.last_daily_low_alert_date = today
                    state.set(
                        "last_daily_low_alert_date", 
                        today
                    )
        
        elif self.alert_sent_low and temperature >= low_reset:
            logger.info("Low temperature recovered.")
            send_email_alert(temperature, humidity, alert_type="recovered_low")
            self.alert_sent_low = False
            state.set("alert_sent_low", False)

        self.hardware.set_led(self.alert_sent_high or self.alert_sent_low)

    def run(self):
        logger.info("[START] Monitoring Started. Press Ctrl + C to stop.")

        try:
            while self._running:
                try:
                    temperature, humidity = self.hardware.read_sensor()

                    if temperature is None or humidity is None:
                        logger.warning(
                            "[SENSOR] Sensor returned an empty string."
                        )
                    
                    else:
                        try:
                            validation = self.validator.validate(
                                temperature,
                                humidity
                            )

                            if not validation.is_valid:
                                logger.warning(
                                    f"[VALIDATOR] Rejected sensor reading: "
                                    f"{validation.reason}"
                                )
                            
                            else:
                                self.process_reading(
                                    temperature,
                                    humidity
                                )

                        except Exception as e:
                            logger.error(
                                f"Processing failure: {e}",
                                exc_info=True
                            )
                            
                except RuntimeError as err:
                    logger.error(f"DHT read error: {err}")
                
                time.sleep(READ_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            logger.info("\n[STOP] Monitoring stopped by user.")

        finally:
            self.hardware.cleanup()

    def _is_time_for_daily_alert(self):
        now = datetime.now()
        target_time = datetime.strptime(DAILY_ALERT_TIME, "%H:%M").time()

        return now.time() >= target_time

    def stop(self):
        logger.info("[STOP] Shutdown signal received.")
        self._running = False
