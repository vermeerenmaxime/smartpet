# pylint: skip-file
from RPi import GPIO
import time


class RGB:
    def __init__(self, pins):
        self.led_red = pins[0]
        self.led_green = pins[1]
        self.led_blue = pins[2]

        GPIO.setup(pins, GPIO.OUT)

    def led_branden(self, colors):

        GPIO.output(self.led_red, colors[0])
        GPIO.output(self.led_green, colors[1])
        GPIO.output(self.led_blue, colors[2])

    def led_knipper(self, colors):

        self.led_branden(colors)

        time.sleep(1)

        self.led_doven()

    def led_doven(self):
        GPIO.output(self.led_red, 0)
        GPIO.output(self.led_green, 0)
        GPIO.output(self.led_blue, 0)

try:
    GPIO.setmode(GPIO.BCM)
    rgb = RGB([4, 17, 27])
    
    while True:
        rgb.led_knipper([1,0,1])
        time.sleep(2)

except KeyboardInterrupt as e:
    print(e)
finally:
    GPIO.cleanup()
    print("Finish")