#! ../pyenv/bin/python3

import atexit
from math import sqrt, floor
import threading
from time import sleep
from coordinates import Coordinate

Coordinate.default_order = 'xy'

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
from Adafruit_MotorHAT import Adafruit_MotorHAT

# There are about 1840 measuring points over the x-axis
# There are about 1760 measuring points over the y-axis
maxMeasuringPointsXaxis = 1760.0
maxMeasuringPointsYaxis = 1760.0

###
# Setting up motors
###

# Set variables
mh = Adafruit_MotorHAT(addr=0x70)

# Motor that goes over the x-axis, the motor itself is stationary
xMotor = mh.getMotor(1)
# Motor that goes over the y-axis, the motor itself is on the moving arm
yMotor = mh.getMotor(2)


def turnOffMotors():
    xMotor.run(Adafruit_MotorHAT.RELEASE)
    yMotor.run(Adafruit_MotorHAT.RELEASE)


# Should the program on the Pi crash, the motors will be stopped
#  See motor hat documentation page 4
atexit.register(turnOffMotors)

###
# Setting up pump

# Relais to pump
GPIO.setup([7], GPIO.OUT)


def pumpOff():
    GPIO.output(7, GPIO.LOW)


def pumpOn():
    GPIO.output(7, GPIO.HIGH)


###
# Measuring
###
# Measuring is done through ports. Each motor has two encoders that pulse when the motor is
# running: e.g. e2Blue is of the encoder of motor 2, connected with a blue wire
# We will use these counts to determine our current position

# Encoders setup, there are two for every dc-motor
GPIO.setup([11, 13, 16, 18], GPIO.IN)

# TODO add updated maxcounts
portToCounterDict = {
    # Measures x-axis. Encoder on stationary motor
    11: 0,  # e1Blue,  MaxCount =
    13: 0,  # e1Green, MaxCount =
    # Measures y-axis. Encoder on moving motor
    16: 0,  # e2Blue,  MaxCount = 869
    18: 0  ## e2Green, MaxCount = 869
}

xCounter = 0
yCounter = 0


def measuringCallback(channel):
    portToCounterDict[channel] += 1
    global xCounter
    xCounter = portToCounterDict[11] + portToCounterDict[13]
    global yCounter
    yCounter = portToCounterDict[16] + portToCounterDict[18]


# TODO add anti-switch bouncing ( if necessary)
# Sincerely I cannot give a list of channels to these functions
GPIO.add_event_detect(11, GPIO.RISING)
GPIO.add_event_callback(11, measuringCallback)
GPIO.add_event_detect(13, GPIO.RISING)
GPIO.add_event_callback(13, measuringCallback)
GPIO.add_event_detect(16, GPIO.RISING)
GPIO.add_event_callback(16, measuringCallback)
GPIO.add_event_detect(18, GPIO.RISING)
GPIO.add_event_callback(18, measuringCallback)


###
# Movement
###

# Sets motor in position (0,0)
def resetPos():
    print("Starting position reset")
    # Ramp both motors up to max speed (255)
    xMotor.run(Adafruit_MotorHAT.BACKWARD)
    for i in range(255):
        xMotor.setSpeed(i)
    yMotor.run(Adafruit_MotorHAT.BACKWARD)
    for i in range(255):
        yMotor.setSpeed(i)

    # Run until we can't go any further
    oldX, oldY = xCounter, yCounter
    xDone, yDone = False, False
    newX, newY = -1, -1
    # TODO Deze stomme while loop eindigt te vroeg! GRRR
    while not xDone and not yDone:
        print("old pos: " + str(oldX) + " & " + str(oldY))
        if oldX - newX == 0:
            xDone = True
            print("xDone!")
            xMotor.run(Adafruit_MotorHAT.RELEASE)
        if oldY - newY == 0:
            yDone = True
            print("yDone!")
            yMotor.run(Adafruit_MotorHAT.RELEASE)
        newX, newY = oldX, oldY
        sleep(0.01)
        oldX, oldY = xCounter, yCounter
        print(str(xDone) + str(yDone) + " so " + str(not xDone and not yDone))
    print("Reset to (0,0) complete")


def setDirection(motor, dist):
    if (dist > 0):
        motor.run(Adafruit_MotorHAT.FORWARD)
    else:
        motor.run(Adafruit_MotorHAT.BACKWARD)


# Preliminary, to be refactored
def drawLine(start, end):
    xDist = end.x - start.x
    yDist = end.y - start.y
    setDirection(xMotor, xDist)
    setDirection(yMotor, yDist)

    # Now set length
    xDist = abs(xDist)
    yDist = abs(yDist)
    if (xDist == 0):
        xMotor.setSpeed(0)
        for i in range(255):
            yMotor.setSpeed(i)
    else:
        speedDif = yDist / xDist
        for i in range(255):
            if (xDist > yDist):
                xMotor.setSpeed(255)
                yMotor.setSpeed(floor(255 * speedDif))
            else:
                xMotor.setSpeed(floor(255 / speedDif))
                yMotor.setSpeed(255)
    length = sqrt(xDist * xDist + yDist * yDist)
    sleep(length)


def printVector(vector):
    print("Casual printing")


def printQueue(vectorQueue):
    print("Starting placeholder printing")
    for vector in vectorQueue:
        printVector(vector)


# Precondition: Starts in bottom left corner
def drawRectangle(length, breadth):
    drawLine(Coordinate(0, 0), Coordinate(x=length, y=0))
    drawLine(Coordinate(length, 0), Coordinate(x=length, y=breadth))
    drawLine(Coordinate(length, breadth), Coordinate(x=0, y=breadth))
    drawLine(Coordinate(x=0, y=breadth), Coordinate(x=0, y=0))


###
# Axial systems
###
# In this project there are three axial systems:
#   - the numpy coordinate system used by the slicer (320 x 320)
#   - the encoder measuring system (1840 x 1760)
#   - the time for the motors at full speed to reach a point in seconds(5 x 6)
# We below the converters (numpy, encoder) and (encoder, time)
# The first is simple, the latter accommodates for ramping and inequality between motors

def numpyToEncoder(numpyCoordinate):
    x = numpyCoordinate[0]
    y = numpyCoordinate[1]
    # Slicer uses a grid system of 320 x 320
    x = x / 320.0
    y = y / 320.0
    x = x * maxMeasuringPointsXaxis
    y = y * maxMeasuringPointsYaxis
    return Coordinate(x, y)


# TODO improve heavily: account for ramping
# To avoid ramping of the dc motor we take the trajectory of a complete vector
#  and steer towards the end. At the end of a vector we stop completely
def encoderToTime(encoderVector):
    print()


def test():
    print("start test")
    print(converter([160.0, 160.0]))
    print("end")

# TODO When you've got water and stuff
# Flushes the tube for 60 seconds (for cleaning)
# def flush_the_tube():
#    GPIO.setup([7], GPIO.OUT)
#    GPIO.output(7, 1)
#    sleep(60)
#    GPIO.cleanup(7)
#    sleep(.2)
