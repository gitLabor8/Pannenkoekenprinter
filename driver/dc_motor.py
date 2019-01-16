#! ../pyenv/bin/python3

import atexit
from math import sqrt, floor
from time import sleep
from collections import deque
from coordinates import Coordinate
from numpy import sign

Coordinate.default_order = 'xy'

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
from Adafruit_MotorHAT import Adafruit_MotorHAT

# Amount of measuring points over the axis
maxMeasuringPointsXaxis = 1500.0
maxMeasuringPointsYaxis = 1450.0
# Time it takes to cover all measuring points with a full speed motor. Numbers acquired through
# statistics. Allows us to compensates for one motor being slower than the other
maxTimeXaxis = 5.99
maxTimeYaxis = 5.76

###
# Setting up motors
###

# Set variables
mh = Adafruit_MotorHAT(addr=0x70)
maxSpeed = 255

# Motor that goes over the x-axis, the motor itself is stationary
xMotor = mh.getMotor(1)
# Motor that goes over the y-axis, the motor itself is on the moving arm
yMotor = mh.getMotor(2)


def turnOffMotors():
    xMotor.setSpeed(0)
    xMotor.run(Adafruit_MotorHAT.RELEASE)
    yMotor.setSpeed(0)
    yMotor.run(Adafruit_MotorHAT.RELEASE)


# Should the program on the Pi crash, the motors will be stopped
#  See motor hat documentation page 4
atexit.register(turnOffMotors)

###
# Setting up pump
###

# Relais to pump
GPIO.setup([7], GPIO.OUT, initial=GPIO.HIGH)


# The relais wants a HIGH to turn the pump and green control light off
def pumpOff():
    GPIO.output(7, GPIO.HIGH)


# The relais wants a LOW to turn the pump and green control light on
def pumpOn():
    GPIO.output(7, GPIO.LOW)


# Should the program on the Pi crash, the motors will be stopped
#  See motor hat documentation page 4
# Note: atexit functions are executed in reversed order
atexit.register(GPIO.cleanup)
atexit.register(pumpOff)

'''
###
# Measuring
###
Measuring is done through ports. Each motor has two encoders that pulse when the motor is
running: e.g. e2Blue is of the encoder of motor 2, connected with a blue wire
We will use these counts to determine our current position
'''

# Encoders setup, there are two for every dc-motor
GPIO.setup([11, 13, 16, 18], GPIO.IN)

portToCounterDict = {
    # Measures x-axis. Encoder on stationary motor
    11: 0,  # e1Blue
    13: 0,  # e1Green
    # Measures y-axis. Encoder on moving motor
    16: 0,  # e2Blue
    18: 0  ## e2Green
}

xCounter = 0
yCounter = 0
# Current position given in the measuring grid
currentPos = Coordinate(0, 0)


# Upon receiving measurement pulse update counters accordingly
def measuringCallback(channel):
    portToCounterDict[channel] += 1
    global xCounter
    xCounter = portToCounterDict[11] + portToCounterDict[13]
    global yCounter
    yCounter = portToCounterDict[16] + portToCounterDict[18]


# Sincerely I cannot give a list of channels to these functions
# Linking measuring pulses to the callback function
GPIO.add_event_detect(11, GPIO.RISING)
GPIO.add_event_callback(11, measuringCallback)
GPIO.add_event_detect(13, GPIO.RISING)
GPIO.add_event_callback(13, measuringCallback)
GPIO.add_event_detect(16, GPIO.RISING)
GPIO.add_event_callback(16, measuringCallback)
GPIO.add_event_detect(18, GPIO.RISING)
GPIO.add_event_callback(18, measuringCallback)

'''
###
# Movement
###
TODO outline these functions
'''


# Sets motor in position (0,0)
# Note: this is the utmost down left position for the motor plus an offset to compensate for the
# round edges of the frying pan
def resetPos():
    print("Starting position reset")
    # Ramp both motors up to max speed
    xMotor.run(Adafruit_MotorHAT.BACKWARD)
    revUpMotor(xMotor, maxSpeed)
    yMotor.run(Adafruit_MotorHAT.BACKWARD)
    revUpMotor(yMotor, maxSpeed)

    # Run until we can't go any further
    oldX, oldY = xCounter, yCounter
    xDone, yDone = False, False
    newX, newY = -1, -1
    sleepTime = 0
    sleepTimeX = 0
    sleepTimeY = 0
    while not xDone or not yDone:
        if oldX - newX == 0 and not xDone:
            xDone = True
            xMotor.run(Adafruit_MotorHAT.RELEASE)
            sleepTimeX = sleepTime
        if oldY - newY == 0 and not yDone:
            yDone = True
            yMotor.run(Adafruit_MotorHAT.RELEASE)
            sleepTimeY = sleepTime
        newX, newY = oldX, oldY
        sleepTime += 0.02
        sleep(0.02)
        oldX, oldY = xCounter, yCounter
    # # Measurement output
    # print("xCounter = " + str(xCounter) + " in " + str(sleepTimeX))
    # print("yCounter = " + str(yCounter) + " in " + str(sleepTimeY))

    # Offset to accommodate for round edges of frying pan
    moveTo(Coordinate(0, 100))
    turnOffMotors()
    global currentPos
    currentPos = Coordinate(0, 0)
    print("Reset to (0,0) complete")


def setDirection(motor, dist):
    if (dist > 0):
        motor.run(Adafruit_MotorHAT.FORWARD)
    else:
        motor.run(Adafruit_MotorHAT.BACKWARD)


# Gradually speeding up the motor
def revUpMotor(motor, speed):
    # Let's try out not revving, prolly faster
    # motor.setSpeed(speed)
    # Ramping method (better for motor condition?)
    for i in range(speed):
        motor.setSpeed(i)


# Goes to the given absolute endpoint
def moveTo(measurePointCoordinate):
    xDist = measurePointCoordinate.x - currentPos.x
    yDist = measurePointCoordinate.y - currentPos.y
    setDirection(xMotor, xDist)
    setDirection(yMotor, yDist)
    print("xdist, ydist = " + str(xDist) + " " + str(yDist))

    # Now we set the length
    if abs(xDist) == 0 and abs(yDist) == 0:
        return
    # The Y-motor is about 4% faster than the X-motor, see statistics in spreadsheet
    speedDif = maxTimeXaxis / maxTimeYaxis

    if (xDist == 0):
        xSpeed = 0
        ySpeed = maxSpeed
    else:
        distDif = abs(yDist) / abs(xDist)
        if (abs(xDist) > abs(yDist)):
            xSpeed = floor(maxSpeed)
            ySpeed = floor(maxSpeed * distDif / speedDif)
        else:
            xSpeed = floor(maxSpeed / distDif)
            ySpeed = floor(maxSpeed / speedDif)
    revUpMotor(xMotor, xSpeed)
    revUpMotor(yMotor, ySpeed)

    # Roll until we aren't getting any closer
    oldXCounter, oldYCounter = xCounter, yCounter
    # Check if we got closer in the last 3 iterations through a circular buffer
    distanceLeftQue = deque(maxlen=2)
    distanceLeftQue.append(pow(xDist, 2) + pow(yDist, 2))
    iteration = 0
    baseAmountOfIterations = 0
    # Make it run for at least 3 steps to accommodate for ramping
    while distanceLeftQue[0] >= distanceLeftQue[-1] or \
            iteration <= max(baseAmountOfIterations, distanceLeftQue.maxlen):
        lengthToGoX = abs(xCounter - oldXCounter - abs(xDist))
        lengthToGoY = abs(yCounter - oldYCounter - abs(yDist))
        sleep(0.004)
        # TODO Possible improvement: other distance metric
        distanceLeft = sqrt(pow(lengthToGoX, 2) + pow(lengthToGoY, 2))
        distanceLeftQue.append(distanceLeft)
        iteration += 1
    turnOffMotors()
    global currentPos
    # TODO Test: measured value <-> expected value
    # # using expected value
    # currentPos = measurePointCoordinate
    # using measured value
    xCoor = currentPos.x + (xCounter - oldXCounter) * sign(xDist)
    yCoor = currentPos.y + (yCounter - oldYCounter) * sign(yDist)
    currentPos = Coordinate(xCoor, yCoor)
    print("currentPos: " + str(currentPos))

    # # How much deviation is caused by the 2-step latency?
    print("circ buff: " + str(distanceLeftQue))
    if distanceLeftQue[0] >= 50:
        print(" Wew, we're way off. Let's find out why!")
        print("  xSpeed: " + str(xSpeed) + " ySpeed: " + str(ySpeed))
    print(" ")


def printQueue(vectorQueue):
    resetPos()
    for vector in vectorQueue:
        # Move to starting position
        moveTo(numpyToEncoder(vector[0]))
        # Start printing
        pumpOn()

        moveTo(numpyToEncoder(vector[vector.__len__() - 1]))
        # for x in range(vector.__len__()):
        #     # Only print every fourth coordinate
        #     if (x % 4) == 0:
        #         moveTo(numpyToEncoder(vector[x]))

        # for coordinate in vector:
        #     moveTo(numpyToEncoder(coordinate))
        pumpOff()


# Precondition: Starts in bottom left corner
def drawRectangle(breadth, height):
    moveTo(Coordinate(currentPos.x, height + currentPos.y))
    moveTo(Coordinate(breadth + currentPos.x, currentPos.y))
    moveTo(Coordinate(currentPos.x, - height + currentPos.y))
    moveTo(Coordinate(- breadth + currentPos.x, currentPos.y))


'''
##
# Axial systems
##
In this project there are two axial systems:
  - the numpy coordinate system used by the slicer (320 x 320)
  - the encoder measuring system (maxMeasuringPointsXaxis x maxMeasuringPointsYaxis)
'''


def numpyToEncoder(numpyCoordinate):
    x = numpyCoordinate[0]
    y = numpyCoordinate[1]
    if x > 320.0 or y > 320.0:
        print("One of these numpy coordinates is larger than 320. We're going out "
              "of bounds. x y " + str(x) + " " + str(y))
    x = x / 320.0
    y = y / 320.0
    x = x * maxMeasuringPointsXaxis
    y = y * maxMeasuringPointsYaxis
    print("Dest Coor: " + str(x) + " " + str(y))
    return Coordinate(x, y)


def test(vectorQueue):
    print("start test")
    # resetPos()
    # drawingRange()
    drawingRange()
    # printQueue(vectorQueue)
    print("end")


# Show the user what the drawing range is by printing
# Also functions as a way to load the tube with fluid
def drawingRange():
    resetPos()
    pumpOn()
    drawRectangle(maxMeasuringPointsXaxis, maxMeasuringPointsYaxis)
    pumpOff()
    resetPos()


# Flushes the tube for 60 seconds (for cleaning)
def flushTube():
    pumpOn()
    sleep(60)
    pumpOff()


dummyVector = [[168.8, 275.28],
               [168.0, 275.28],
               [167.2, 275.28],
               [166.4, 275.28],
               [165.6, 275.28],
               [164.8, 275.28],
               [164.0, 275.28],
               [163.2, 275.28],
               [162.4, 275.28],
               [161.6, 275.28],
               [160.8, 275.28],
               [160.0, 275.28],
               [159.2, 275.28],
               [158.4, 275.28],
               [157.6, 275.28],
               [156.8, 275.28],
               [156.0, 275.28],
               [155.2, 275.28],
               [154.4, 275.28],
               [153.6, 275.28],
               [152.8, 275.28],
               [152.0, 275.28],
               [151.2, 275.28],
               [150.4, 275.28],
               [149.6, 275.28],
               [149.52, 275.2],
               [149.52, 274.4],
               [149.52, 273.6],
               [149.52, 272.8],
               [149.52, 272.0],
               [149.52, 271.2],
               [149.52, 270.4],
               [149.52, 269.6],
               [149.52, 268.8],
               [149.52, 268.0],
               [149.52, 267.2],
               [149.52, 266.4],
               [149.52, 265.6],
               [149.52, 264.8],
               [149.52, 264.0],
               [149.52, 263.2],
               [149.52, 262.4],
               [149.52, 261.6],
               [149.52, 260.8],
               [149.52, 260.],
               [149.52, 259.2],
               [149.52, 258.4],
               [149.52, 257.6],
               [149.52, 256.8],
               [149.52, 256.],
               [149.52, 255.2],
               [149.52, 254.4],
               [149.52, 253.6],
               [149.52, 252.8],
               [149.52, 252.],
               ]
