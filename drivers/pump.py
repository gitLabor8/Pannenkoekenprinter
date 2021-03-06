###
# Sets up the pump and provides handlers to hide hardware details
###

import atexit
from time import sleep
from RPi import GPIO

GPIO.setmode(GPIO.BOARD)

# Relais to pump
GPIO.setup([7], GPIO.OUT, initial=GPIO.HIGH)


# The relais wants a HIGH to turn the pump and green control light off
def off():
    GPIO.output(7, GPIO.HIGH)
    # print("pump off")
    # print("Pump is currently disabled")


# The relais wants a LOW to turn the pump and green control light on
def on():
    GPIO.output(7, GPIO.LOW)
    # print("pump on!")
    # print("Pump is currently disabled")

# Should the program on the Pi crash, the motors will be stopped
#  See motor hat documentation page 4
# Note: atexit functions are executed in reversed order
atexit.register(GPIO.cleanup)
atexit.register(off)


# Flushes the tube for 10 minutes (for cleaning)
def flushTube():
    on()
    sleep(60*10)
    off()
