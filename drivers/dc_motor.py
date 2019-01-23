#! ../pyenv/bin/python3

from drivers import pump
from drivers.dc_motor_adafruit_wrapper import MotorWrapper
from drivers.path import Path
import atexit
from math import sqrt, floor
from time import sleep
from collections import deque
from coordinates import Coordinate
from numpy import sign

# from sympy.geometry import *
# from shapely.geometry import *

Coordinate.default_order = 'xy'

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
from Adafruit_MotorHAT import Adafruit_MotorHAT

# Amount of measuring points over the axis
maxMeasuringPointsXaxis = 1300.0
maxMeasuringPointsYaxis = 1450.0
# Time it takes to cover all measuring points with a full speed motor. Numbers acquired through
# statistics. Allows us to compensates for one motor being slower than the other
maxTimeXaxis = 5.99
maxTimeYaxis = 5.76

''''
###
# Setting up motors
###
'''

# Motor that goes over the x-axis, the motor itself is stationary
xMotor = MotorWrapper(1)
# Motor that goes over the y-axis, the motor itself is on the moving arm
yMotor = MotorWrapper(2)
maxSpeed = 255


def turnOffMotors():
    xMotor.turnOff()
    yMotor.turnOff()


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
'''


# Sets motor in position (0,0) of the drawing frame
def resetPos():
    # print("Starting position reset")
    # Ramp both motors up to max speed backwards
    xMotor.setDirection(-1)
    xMotor.setSpeed(maxSpeed)
    yMotor.setDirection(-1)
    yMotor.setSpeed(maxSpeed)

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
    moveTo(Coordinate(45, 100))
    global currentPos
    currentPos = Coordinate(0, 0)
    # print("Reset to (0,0) complete")


import time


# Goes to the given absolute endpoint
def moveTo(end):
    global currentPos
    start = currentPos
    # The path that we will ideally follow
    path = Path(start, end)
    xMotor.setDirection(path.xDist)
    yMotor.setDirection(path.yDist)

    # The Y-motor is about 4% faster than the X-motor, see statistics in spreadsheet
    speedDif = maxTimeXaxis / maxTimeYaxis
    # Now we calculate base speeds
    if path.xDist == 0 and path.yDist == 0:
        return
    if path.xDist == 0:
        xSpeedBase = 0
        ySpeedBase = maxSpeed
    else:
        distDif = abs(path.yDist) / abs(path.xDist)
        if (abs(path.xDist) > abs(path.yDist)):
            xSpeedBase = floor(maxSpeed)
            ySpeedBase = floor(maxSpeed * distDif / speedDif)
        else:
            xSpeedBase = floor(maxSpeed / distDif)
            ySpeedBase = floor(maxSpeed / speedDif)

    # We are using threads to steer the motors, because otherwise one motor runs
    # still when the other is gaining speed
    # Should things go wacky, we need to be able to adjust our movements
    xCounterOld, yCounterOld = xCounter, yCounter
    # Keeps track of how close we've been to our goal. Acts as emergency stop
    # should we overshoot
    distLeftCircBuffer = deque(maxlen=3)
    finished = False
    while not finished:
        try:
            # Can be 0.004
            # sleep(0.004)
            # Update current position
            xCoor = start.x + (xCounter - xCounterOld) * sign(path.xDist)
            yCoor = start.y + (yCounter - yCounterOld) * sign(path.yDist)
            currentPos = Coordinate(xCoor, yCoor)
            # Calculate how far we still need to go
            xDistanceLeft = abs(xCounter - xCounterOld - abs(path.xDist))
            yDistanceLeft = abs(yCounter - yCounterOld - abs(path.yDist))
            distanceLeft = sqrt(pow(xDistanceLeft, 2) + pow(yDistanceLeft, 2))
            distLeftCircBuffer.append(distanceLeft)
            # Calculate where we are supposed to be now
            expectedPos = path.expectedPos(distanceLeft)
            # Adjust speed accordingly
            xMod = speedModifier(currentPos.x, expectedPos.x)
            yMod = speedModifier(currentPos.y, expectedPos.y)
            xSpeed = floor(xMod * min(xSpeedBase, speedNearEnd(xDistanceLeft)))
            ySpeed = floor(yMod * min(ySpeedBase, speedNearEnd(yDistanceLeft)))
            startTime = time.time()
            xMotor.speedUp(xSpeed)
            yMotor.speedUp(ySpeed)
            endTime = time.time()
            print("speeds: " + str(xMotor.speed) + " " + str(yMotor.speed))
            # print("Time motors: " + str(endTime - startTime))
            print("distanceLeft:" + str(distanceLeft))
            finished = distanceLeft < 5
            if distLeftCircBuffer[0] + 1 < distLeftCircBuffer[-1] \
                    and distLeftCircBuffer.__len__() == distLeftCircBuffer.maxlen:
                print("Emergency exit, we went too far: " + str(distLeftCircBuffer))
                finished = True
        except KeyboardInterrupt:
            print("currentPos:  " + str(currentPos.x) + " " + str(currentPos.y))
            print("expectedPos: " + str(expectedPos.x) + " " + str(expectedPos.y))
            print("baseSpeeds:  " + str(xSpeedBase) + " " + str(ySpeedBase))
            print("distsLeft:   " + str(xDistanceLeft) + " " + str(yDistanceLeft))
            print("mods:        " + str(xMod) + " " + str(yMod))
            print("speeds:      " + str(xSpeed) + " " + str(ySpeed))
            break
    turnOffMotors()

    print("currentPos: " + str(currentPos))

    # # How much deviation is caused by the 2-step latency?
    # print("circ buff: " + str(distanceLeftQue))
    # if distanceLeftQue[0] >= 50:
    #     print(" Wew, we're way off. Let's find out why!")
    #     print("  xSpeed: " + str(xSpeed) + " ySpeed: " + str(ySpeed))
    print(" ")


# When the motor is almost there, it should gradually slow down
def speedNearEnd(distance):
    if distance > 50:
        return maxSpeed
    elif distance < 10:
        return 20
    slowDown = 47 / 8 * distance - 310 / 8
    # print("Slowdown: " + str(slowDown))
    return slowDown


# Calculates the boost a motor needs to keep the printer head on the expected path
# Expects two _numbers_ not two coordinates
# TODO Scale these
def speedModifier(currentPos, expectedPos):
    margin = 1
    if currentPos < expectedPos - margin:
        return 1.0
    elif currentPos > expectedPos + margin:
        return 0.8
    return 0.9


def printVectorQueue(vectorQueue):
    resetPos()
    for vector in vectorQueue:
        # Move to starting position
        moveTo(numpyToEncoder(vector[0]))
        # Start printing
        pump.on()
        # # Print only the line from the first to the last coor
        # moveTo(numpyToEncoder(vector[vector.__len__() - 1]))

        # Print every coor
        for x in range(vector.__len__()):
            moveTo(numpyToEncoder(vector[x]))

            for coordinate in vector:
                moveTo(numpyToEncoder(coordinate))
        pump.off()
    resetPos()


# Converts numpy coordinates (320x320) to the grid used by
#  our measuring system (maxMeasuringPointsXaxis x maxMeasuringPointsYaxis)
def numpyToEncoder(numpyCoordinate):
    x = numpyCoordinate[0]
    y = numpyCoordinate[1]
    if x > 320.0 or y > 320.0:
        print("numpyToEncoder: One of the numpy coordinates is larger than 320. "
              "We're going out of bounds. x, y: " + str(x) + ", " + str(y))
    x = x / 320.0
    y = y / 320.0
    x = x * maxMeasuringPointsXaxis
    y = y * maxMeasuringPointsYaxis
    print("Dest Coor: " + str(x) + " " + str(y))
    return Coordinate(x, y)


def test(vectorQueue):
    print("start test")
    resetPos()
    # print(str(expectedCoorGenerator(Coordinate(0, 0), Coordinate(3, 4), 0.1)))
    # drawingRange()
    moveTo(Coordinate(maxMeasuringPointsXaxis, maxMeasuringPointsYaxis))
    # pumpOn()
    # drawRectangle(maxMeasuringPointsXaxis-2*200, maxMeasuringPointsYaxis-2*200)
    # pumpOff()
    # printVectorQueue(squareInSquareVectorQueue)

    print("end")


# Precondition: Starts in bottom left corner
def drawRectangle(breadth, height):
    moveTo(Coordinate(currentPos.x, height + currentPos.y))
    moveTo(Coordinate(breadth + currentPos.x, currentPos.y))
    moveTo(Coordinate(currentPos.x, - height + currentPos.y))
    moveTo(Coordinate(- breadth + currentPos.x, currentPos.y))


# Show the user what the max drawing range is by printing it
# Also functions as a way to load the tube with fluid
def drawingRange():
    resetPos()
    pump.on()
    drawRectangle(maxMeasuringPointsXaxis, maxMeasuringPointsYaxis)
    pump.off()
    resetPos()


# Hardcoded first-print test
squareInSquareVectorQueue = [[[0., 0.],
                              [0., 320.],
                              [320., 320.],
                              [320., 0],
                              [0., 0.]
                              ],
                             [[80., 80.],
                              [240., 80.],
                              [240., 240.],
                              [80., 240.],
                              [80., 80.]
                              ]]

# First part of an eiffeltower vector
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
