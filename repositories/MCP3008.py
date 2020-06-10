# pylint: skip-file
import RPi.GPIO as GPIO
import spidev
import time


class MCP3008:
    def __init__(self, bus=0, device=0):
        GPIO.setmode(GPIO.BCM)
        # spidev object initialiseren
        self.spi = spidev.SpiDev()
        # open bus 0, device 0
        self.spi.open(bus, device)
        # stel klokfrequentie in op 100kHz
        self.spi.max_speed_hz = 10 ** 6

    def read_channel(self, ch):
        # commandobyte samenstellen
        channel = ch << 4 | 128
        bytes_out = [0b00000001, channel, 0b00000000]
        value_channel = self.spi.xfer(bytes_out)
        byte1 = value_channel[1]
        byte2 = value_channel[2]
        result_channel = byte1 << 8 | byte2
        return result_channel


# try:
#     GPIO.cleanup()
#     GPIO.setmode(GPIO.BCM)
#     MCP = MCP3008()

#     while True:

#         waarde_ldr = MCP.read_channel(0)
#         print(waarde_ldr)
#         time.sleep(1)

# except KeyboardInterrupt as e:
#     print(e)
# finally:
#     # servo.stop()
#     GPIO.cleanup()
#     print("Finish")
