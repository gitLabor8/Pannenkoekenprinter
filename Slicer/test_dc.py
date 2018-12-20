#! ../pyenv/bin/python

import atexit
import math
import threading
from time import sleep

#import RPi.GPIO as GPIO
#from adafruit_motorkit import MotorKit
#kit = MotorKit()
#
#kit.motor1.throttle = .3
#sleep(1)
#kit.motor1.throttle = 0
from Adafruit_MotorHAT import Adafruit_MotorHAT

# Set variables
#mh = Adafruit_MotorHAT(addr=0x6F)
mh = Adafruit_MotorHAT(addr=0x70)
pos_x = 0
pos_y = 0
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup([7], GPIO.OUT)

run_motorspeed = 30

# Motor that goes over the x-axis
xMotor = mh.getMotor(1)
# Motor that goes over the y-axis
yMotor = mh.getMotor(2)

def turnOffMotors():
    xMotor.run(Adafruit_MotorHAT.RELEASE)
    yMotor.run(Adafruit_MotorHAT.RELEASE)
    
# Should the program on the Pi crash, the motors will be stopped
#  See motor hat documentation page 4
atexit.register(turnOffMotors)

# Test motors alternatingly
currentMotor = xMotor
while (True):
    print ("Forward!")
    currentMotor.run(Adafruit_MotorHAT.FORWARD)

    print ("\tSpeed up...")
    for i in range(255):
        currentMotor.setSpeed(i)
        sleep(0.01)
        
    print ("\tSlow down...")
    for i in reversed(range(255)):
        currentMotor.setSpeed(i)
        sleep(0.01)

    print ("Backward! ")
    currentMotor.run(Adafruit_MotorHAT.BACKWARD)

    print ("\tSpeed up...")
    for i in range(255):
        currentMotor.setSpeed(i)
        sleep(0.01)

    print ("\tSlow down...")
    for i in reversed(range(255)):
        currentMotor.setSpeed(i)
        sleep(0.01)

    print ("Release")
    currentMotor.run(Adafruit_MotorHAT.RELEASE)
    sleep(1.0)
    
    # Switching testing motor
    if (currentMotor == xMotor):
        currentMotor = yMotor
    else:
        currentMotor = xMotor
