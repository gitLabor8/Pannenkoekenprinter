###
# Converts vectors into movement
###

from drivers import pump
from drivers.dc_motor_adafruit_wrapper import MotorWrapper
from drivers.path import Path
from drivers.motorThread import MotorThread
from math import sqrt, floor
from time import sleep
from collections import deque
from coordinates import Coordinate
from numpy import sign
import queue

Coordinate.default_order = 'xy'

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
from Adafruit_MotorHAT import Adafruit_MotorHAT

# Amount of measuring points over the axis
maxMeasuringPointsXaxis = 1450.0
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
# Highest number that the motor accepts
maxSpeed = 255
# Lowest speed that makes the arms move
minSpeed = 85


def turnOffMotors():
    xMotor.turnOff()
    yMotor.turnOff()


# We are using threads to steer the motors, because we want to control them
# simultaneously
xSpeedQ, ySpeedQ = queue.LifoQueue(), queue.LifoQueue()
xThread = MotorThread(xMotor, xSpeedQ)
yThread = MotorThread(yMotor, ySpeedQ)
xThread.setName("xMotorThread")
yThread.setName("yMotorThread")
xThread.start()
yThread.start()

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
# Basic Movement
###
'''


# Sets motor in position (0,0) of the drawing frame
def resetPos():
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
    while not xDone or not yDone:
        if oldX - newX == 0 and not xDone:
            xDone = True
            xMotor.run(Adafruit_MotorHAT.RELEASE)
        if oldY - newY == 0 and not yDone:
            yDone = True
            yMotor.run(Adafruit_MotorHAT.RELEASE)
        newX, newY = oldX, oldY
        sleepTime += 0.02
        sleep(0.02)
        oldX, oldY = xCounter, yCounter

    # Offset to accommodate for round edges of frying pan
    currentPos = Coordinate(0, 0)
    moveTo(Coordinate(100, 200))
    global currentPos
    currentPos = Coordinate(0, 0)
    print("Reset to (0,0) complete")


# When the motor is almost there, it should gradually slow down
def speedNearEnd(distance: float):
    if distance > 200:
        return maxSpeed
    elif distance < 10:
        return minSpeed
    slowDown = 1 * distance + 55
    return slowDown


# Calculates the boost a motor needs to keep the printer head on the expected path
# Expects two _numbers_ not two coordinates
# orientation true = positive: the coordinate must increase
def speedModifier(currentPos: float, expectedPos: float, orientation: bool):
    margin = 1
    diff = currentPos - expectedPos
    # Going in positive direction
    if orientation:
        # We go too fast -> slow down
        if diff > margin:
            return max(0.8, -0.009 * diff + 0.9)
        # We go too slow -> speed up
        elif diff < -margin:
            return min(1.0, -0.009 * diff + 0.9)
        return 0.9
    # Going in negative direction
    else:
        diff = -diff
        # We go too slow -> speed up
        if diff > margin:
            return max(0.8, -0.009 * diff + 0.9)
        # We go too fast -> slow down
        elif diff < -margin:
            return min(1.0, -0.009 * diff + 0.9)
        return 0.9


# Goes to the given absolute endpoint
def moveTo(end):
    global currentPos
    start = currentPos
    # The path that we will ideally follow
    path = Path(start, end)
    # print(str(path))
    xFinished, yFinished = False, False
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

    # If the distance that needs to be traversed is negligible, the motor will not
    #  have a high enough minimal speed. Therefore we ignore the transformation
    if xSpeedBase < minSpeed:
        xFinished = True
    if ySpeedBase < minSpeed:
        yFinished = True

    # Should things go wacky, we need to be able to adjust our movements
    xCounterOld, yCounterOld = xCounter, yCounter
    lowestDist = 1000

    # Keeps track of how close we've been to our goal. Acts as emergency stop
    # should we overshoot
    distLeftCircBuffer = deque(maxlen=3)
    while not xFinished or not yFinished:
        sleep(0.04)
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
        if xFinished:
            xMod = 0
        else:
            xMod = speedModifier(currentPos.x, expectedPos.x, path.xOrientation)
            xFinished = xDistanceLeft < 5
        if yFinished:
            yMod = 0
        else:
            yMod = speedModifier(currentPos.y, expectedPos.y, path.yOrientation)
            yFinished = yDistanceLeft < 5
        xSpeed = floor(xMod * min(xSpeedBase, speedNearEnd(xDistanceLeft)))
        ySpeed = floor(yMod * min(ySpeedBase, speedNearEnd(yDistanceLeft)))
        xSpeedQ.put(xSpeed)
        ySpeedQ.put(ySpeed)
        lowestDist = min(distanceLeft, lowestDist)

        # Prevent sloppy edges
        if distanceLeft < 60:
            pump.off()
            xFinished, yFinished = True, True
        # Emergency exit should we go past our point
        if distLeftCircBuffer[0] + 1 < distLeftCircBuffer[-1] \
                and distLeftCircBuffer.__len__() == distLeftCircBuffer.maxlen:
            print("Emergency exit, we went too far: " + str(distLeftCircBuffer))
            xFinished, yFinished = True, True

    turnOffMotors()


'''
###
# Printing more than one line
###
'''


# The encoders have about 2% measuring error. Every once in a while we need to
# reset to accommodate for this
def measuringCorrection(lastResetCount: int):
    global xCounter
    global yCounter
    resetCount = floor((xCounter + yCounter) / 8000)

    if lastResetCount < resetCount:
        resetPos()
    return resetCount


# Prints my own made coordinate arrays. These are test images to check if the
# motors work correctly. Work on our own coordinate grid. A vector is
def printVectorArray(vectorArray):
    resetPos()
    resetCounter = 0
    for vector in vectorArray:
        resetCounter = measuringCorrection(resetCounter)
        print("start printing vector")
        moveTo(vector[0])
        # Print every coordinate in the vector, except the first, since we are
        # already there
        for coordinate in vector[1:]:
            pump.on()
            moveTo(coordinate)
        pump.off()
    resetPos()


'''
###
# Draw the maximum drawing range
###
'''


# Precondition: Starts in bottom left corner
def rectangle(breadth, height):
    return [Coordinate(currentPos.x, currentPos.y),
            Coordinate(breadth + currentPos.x, currentPos.y),
            Coordinate(breadth + currentPos.x, height + currentPos.y),
            Coordinate(currentPos.x, height + currentPos.y),
            Coordinate(currentPos.x, currentPos.y)
            ]


# Show the user what the max drawing range is by printing it
# Also functions as a way to load the tube with fluid
def drawingRange():
    vectorArray = [rectangle(maxMeasuringPointsXaxis, maxMeasuringPointsYaxis)]
    printVectorArray(vectorArray)
    print("Done with drawing range")
