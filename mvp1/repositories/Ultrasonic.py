# wget https://bitbucket.org/MattHawkinsUK/rpispy-misc/raw/master/python/ultrasonic_1.py
# sudo python ultrasonic_1.py
# https://www.raspberrypi-spy.co.uk/2012/12/ultrasonic-distance-measurement-using-python-part-1/

# pylint: skip-file
from RPi import GPIO
import time


class Ultrasonic:

    def __init__(self, pins):

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pins[0], GPIO.OUT)
        GPIO.setup(pins[1], GPIO.IN)

    def meet(self):
        # set Trigger to HIGH
        GPIO.output(pins[0], 1)

        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(pins[0], 0)

        StartTime = time.time()
        StopTime = time.time()

        # save StartTime
        while GPIO.input(pins[1]) == 0:
            StartTime = time.time()

        # save time of arrival
        while GPIO.input(pins[1]) == 1:
            StopTime = time.time()

        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (TimeElapsed * 34300) / 2

        return distance



 
def distance(trigger, echo):

    # set Trigger to HIGH
    GPIO.output(trigger, 1)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)

    GPIO.output(trigger, 0)

    StartTime = time.time()
    StopTime = time.time()
    
    # save StartTime
    while GPIO.input(echo) == 0:
        StartTime = time.time()
    
    # save time of arrival
    while GPIO.input(echo) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s) 17150
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance



try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(2, GPIO.OUT)
    GPIO.setup(3, GPIO.IN)
    while True:
        
        dist_lang_1 = distance(2,3)
        print(dist_lang_1)
        time.sleep(1)
    

except KeyboardInterrupt as e:
    print(e)
finally:
    GPIO.cleanup()
    print("Finish")
