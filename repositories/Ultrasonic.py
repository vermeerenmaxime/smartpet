import RPi.GPIO as gpio
import time

class Ultrasonic:

    def __init__(self,pins):
        self.pin_out = pins[0]
        self.pin_in = pins[1]


    def meten(self,measure="cm"):
        try:
            gpio.setmode(gpio.BCM)
            gpio.setup(self.pin_out, gpio.OUT)
            gpio.setup(self.pin_in, gpio.IN)
            
            gpio.output(self.pin_out, False)
            while gpio.input(self.pin_in) == 0:
                nosig = time.time()

            while gpio.input(self.pin_in) == 1:
                sig = time.time()

            tl = sig - nosig

            if measure == 'cm':
                distance = tl / 0.000058
            elif measure == 'in':
                distance = tl / 0.000148
            else:
                print('improper choice of measurement: in or cm')
                distance = None

            gpio.cleanup()
            return distance
        except:
            distance = 100
            gpio.cleanup()
            return distance

		


# try:
#     sensor_ultrasonic = Ultrasonic([2,3])
#     while True:
#         time.sleep(1)
#         print(sensor_ultrasonic.meten())
# except KeyboardInterrupt as ex:
#     print(ex)
# finally:
#     pass