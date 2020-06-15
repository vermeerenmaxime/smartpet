# pylint: skip-file
from RPi import GPIO
import time
import os
import subprocess

from subprocess import check_output


def geef_ip(choice):
    ips = check_output(['hostname', '--all-ip-addresses'])
    ips = str(ips)
    ip = ips.strip("b'").split(" ")
    return ip[choice]


class LCD:

    def __init__(self, pins):
        self.E = pins[0]
        self.RS = pins[1]

        self.databits = [pins[9], pins[8], pins[7], pins[6], pins[5],
                         pins[4], pins[3], pins[2]]

        self.tekens = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pins, GPIO.OUT)

        GPIO.output(self.E, 0)
        GPIO.output(self.RS, 0)
        for i in range(2, 10):
            GPIO.output(pins[i], 0)

    def send_character(self, char):
        GPIO.output(self.RS, 1)  # Teken versturen DUS 1
        GPIO.output(self.E, 1)  # hoog

        self.set_data_bits(char)

        GPIO.output(self.E, 0)  # laag, nu verstuurd hij de bytes

        time.sleep(0.01)

    def send_instruction(self, byte):
        GPIO.output(self.RS, 0)  # Instructie versturen DUS 0
        GPIO.output(self.E, 1)  # hoog

        self.set_data_bits(byte)

        GPIO.output(self.E, 0)  # laag, nu verstuurd hij de bytes

        time.sleep(0.01)

    def set_data_bits(self, byte):
        mask = 0x80
        # Voor alle 8 data pinnen
        for i in range(0, 8):
            if (byte & mask) > 0:
                GPIO.output(self.databits[i], 1)
            else:
                GPIO.output(self.databits[i], 0)
            mask >>= 1

    def write_message(self, message):
        if(message == "CLEAR"):
            print("** Wis alles op het LCD **")
            self.init_LCD()

        elif(len(message) > 0):

            characters = list(message)
            for char in characters:
                char_ascii = ord(char)
                self.tekens += 1
                if self.tekens > 16 and self.tekens < 18:
                    display.second_row()
                self.send_character(char_ascii)

                if self.tekens > 32:
                    display.scroll("LEFT")
                    display.long_delay()
                if self.tekens > 56:
                    self.tekens = 0
                    display.init_LCD()
        else:
            print("** Bericht moet langer zijn dan 0 tekens **")

    def write_status(self):
        self.init_LCD()

        # characters = list(geef_ip(0))
        # for char in characters:
        #     char_ascii = ord(char)
        #     self.tekens += 1
        #     self.send_character(char_ascii)

        # self.second_row()

        characters = list(geef_ip(1))
        for char in characters:
            char_ascii = ord(char)
            self.tekens += 1
            self.send_character(char_ascii)

    def function_set(self):
        self.send_instruction(56)

    def display_on(self):
        self.send_instruction(15)

    def clear_LCD(self):
        self.send_instruction(1)

    def cursor_home(self):
        self.send_instruction(128)

    def init_LCD(self):
        self.function_set()
        self.display_on()
        self.clear_LCD()

    def second_row(self):
        self.send_instruction(192)

    def scroll(self, direction):
        if(direction.upper() == "LEFT"):
            self.send_instruction(24)
        elif(direction.upper() == "RIGHT"):
            self.send_instruction(28)
        else:
            raise ValueError("Wrong direction given")

    def short_delay(self):
        time.sleep(0.01)

    def long_delay(self):
        time.sleep(0.5)

    def convert_bin_dec(self, bin_list):
        bin_string = ""
        for bit in bin_list:
            bin_string += str(bit)

        return int(bin_string, 2)


# try:
#     display = LCD([20, 18, 16, 12, 25, 24, 23, 26, 19, 13])
#     display.init_LCD()
#     while True:
#         display.write_status()
#         #display.write_message("hoi")
#         print(geef_ip(0))
#         time.sleep(2)
# except KeyboardInterrupt as e:
#     print(e)
# finally:
#     GPIO.cleanup()
#     print("Finish")
