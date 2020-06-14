# pylint: skip-file
import RPi.GPIO as GPIO
import time

class Servo:

    def __init__(self, pin, speed=50):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)

        self.servo = GPIO.PWM(pin, 50)

    def start(self):
        self.servo.start(6)

    def start_links(self):
        self.servo.start(12)

    def stop(self):
        self.servo.stop()



# try:

#     servo = Servo(21)
#     servo.start()
#     while True:
#         time.sleep(2)

# except KeyboardInterrupt as e:
#     print(e)
# finally:
#     GPIO.cleanup()
#     print("Finish")