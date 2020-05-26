# pylint: skip-file
import RPi.GPIO as GPIO
import spidev
import time

# pins
pin_servo = 21


class MCP3008:
    def __init__(self, bus=0, device=0):
        # spidev object initialiseren
        self.spi = spidev.SpiDev()
        # open bus 0, device 0
        self.spi.open(bus, device)
        # stel klokfrequentie in op 100kHz
        self.spi.max_speed_hz = 10 ** 5

    def read_channel(self, ch):
        # commandobyte samenstellen
        channel = ch << 4 | 128
        bytes_out = [0b00000001, channel, 0b00000000]
        value_channel = self.spi.xfer(bytes_out)
        byte1 = value_channel[1]
        byte2 = value_channel[2]
        result_channel = byte1 << 8 | byte2
        return result_channel


try:
    GPIO.cleanup()
    #MCP = MCP3008()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_servo, GPIO.OUT)

    servo = GPIO.PWM(pin_servo, 50)
    servo.start(6)

    while True:
        # GPIO.output(pin_servo, 1)
        # 0 graden (neutraal)
        # servo.ChangeDutyCycle(3)
        print(0)
        time.sleep(5)

        # -90 graden (rechts)
        # GPIO.output(pin_servo, 0)
        # servo.ChangeDutyCycle(11)
        # print(-90)
        # time.sleep(5)

        # # 0 graden (neutraal)
        # servo.ChangeDutyCycle(6)
        # print(0)
        # time.sleep(1)

        # # 90 graden (links)
        # servo.ChangeDutyCycle(11)
        # print(90)
        # time.sleep(1)
        # waarde_ldr = MCP.read_channel(0)
        # print(waarde_ldr)
        # time.sleep(0.1)

except KeyboardInterrupt as e:
    print(e)
finally:
    # servo.stop()
    GPIO.cleanup()
    print("Finish")
