import platform

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
    
        if HARDWARE_AVAILABLE:
            self.dht_device = adafruit_dht.DHT22(board.D4)

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.led_pin, GPIO.OUT)
            GPIO.output(self.led_pin, GPIO.LOW)

            self.lcd = CharLCD('PCF8574', 0x27)
        else:
            print("[INFO] Running in development mode (no hardware detected)")

    def read_sensor(self):
        if HARDWARE_AVAILABLE:
            return self.dht_device.temperature, self.dht_device.humidity
        else:
            return 24.0, 50.0
    
    def set_led(self, state: bool):
        if HARDWARE_AVAILABLE:
            GPIO.ouput(self.led_pin, GPIO.HIGH if state else GPIO.LOW)
    
    def update_lcd(self, temp, hum):
        if HARDWARE_AVAILABLE:
            self.lcd.clear()
            self.lcd.write_string(f"Temp: {temp:.1f}C")
            self.lcd.crlf()
            self.lcd.write_string(f"Hum : {hum:.1f}%")
    
    def cleanup(self):
        if HARDWARE_AVAILABLE:
            self.lcd.clear()
            GPIO.cleanup
            self.dht_device.exit()