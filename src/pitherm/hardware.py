import platform
from src.pitherm.config import ALLOW_FAKE_HARDWARE

HARDWARE_AVAILABLE = False

try:
    if platform.system() == "Linux":
        import adafruit_dht
        import board
        import RPi.GPIO as GPIO
        from RPLCD.i2c import CharLCD

        HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False

class HardwareController:
    def __init__(self):
        self.dht_device = None
        self.lcd = None
        self.led_pin = 17
        self.hardware_ready = False

        if not HARDWARE_AVAILABLE:
            print("[WARN] Hardware libraries not available.")
            return

        try:
            self.dht_device = adafruit_dht.DHT22(board.D4)

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.led_pin, GPIO.OUT)
            GPIO.output(self.led_pin, GPIO.LOW)

            self.lcd = CharLCD('PCF8574', 0x27)

            test_temp = self.dht_device.temperature
            test_hum = self.dht_device.humidity

            if test_temp is None or test_hum is None:
                raise RuntimeError("Initial DHT read returned None")

            self.lcd.clear()
            self.lcd.write_string("PiTherm Ready")

            self.hardware_ready = True
            print("[OK] Hardware initialized successfully.")

        except Exception as e:
            print("[WARN] Hardware initialization failed:", e)
            self.dht_device = None
            self.lcd = None
            self.hardware_ready = False

    def read_sensor(self):
        dht_device = self.dht_device

        if self.hardware_ready and dht_device is not None:
            return dht_device.temperature, dht_device.humidity

        if ALLOW_FAKE_HARDWARE:
            print("[WARN] Using fake hardware reading.")
            return 24.0, 50.0

        raise RuntimeError("Hardware is not ready and fake hardware is disabled.")

    def set_led(self, state: bool):
        if self.hardware_ready:
            GPIO.output(self.led_pin, GPIO.HIGH if state else GPIO.LOW)

    def update_lcd(self, temp, hum):
        lcd = self.lcd

        if self.hardware_ready and lcd is not None:
            lcd.clear()
            lcd.write_string(f"Temp: {temp:.1f}C")
            lcd.crlf()
            lcd.write_string(f"Hum : {hum:.1f}%")

    def cleanup(self):
        lcd = self.lcd
        dht_device = self.dht_device

        if self.hardware_ready and lcd is not None and dht_device is not None:
            lcd.clear()
            GPIO.cleanup()
            dht_device.exit()
