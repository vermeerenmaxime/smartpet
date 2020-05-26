#!/usr/bin/python
 
import spidev
import time
 
spi = spidev.SpiDev()
spi.open(0,0)
 
def read_spi(channel):
  spidata = spi.xfer2([1,(8+channel)<<4,0])
  return ((spidata[1] & 3) << 8) + spidata[2]
 
try:
  while True:
    channeldata = read_spi(0)
    print("Waarde = {}".format(channeldata))
    time.sleep(.1)
 
except KeyboardInterrupt:
  spi.close()