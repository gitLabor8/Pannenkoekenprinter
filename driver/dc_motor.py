#! ../pyenv/bin/python3

import atexit
from math import sqrt, floor
from time import sleep
from collections import deque
from coordinates import Coordinate

Coordinate.default_order = 'xy'

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
from Adafruit_MotorHAT import Adafruit_MotorHAT

# Amount of measuring points over the axis
maxMeasuringPointsXaxis = 1400.0
maxMeasuringPointsYaxis = 1400.0
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
GPIO.setup([15], GPIO.OUT, initial=GPIO.LOW)


def pumpOff():
    GPIO.output(15, GPIO.LOW)


def pumpOn():
    GPIO.output(15, GPIO.HIGH)


# Should the program on the Pi crash, the motors will be stopped
#  See motor hat documentation page 4
atexit.register(pumpOff)
# Note: if GPIO.cleanup() is run atexit (as recommended by tutorials)
#   the GPIO port will be turned into an input port, resulting in the relais/pump being on
#   This does yield a warning about the channel already being in use

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
    # moveTo(Coordinate(0, 100))
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
    xDist = abs(xDist)
    yDist = abs(yDist)
    if xDist == 0 and yDist == 0:
        return
    # The Y-motor is about 4% faster than the X-motor, see statistics in spreadsheet
    speedDif = maxTimeXaxis / maxTimeYaxis

    if (xDist == 0):
        xSpeed = 0
        ySpeed = maxSpeed
    else:
        distDif = yDist / xDist
        if (xDist > yDist):
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
    distanceLeftQue.append(xDist + yDist)
    iteration = 0
    baseAmountOfIterations = 0
    # Make it run for at least 3 steps to accommodate for ramping
    while distanceLeftQue[0] >= distanceLeftQue[-1] or \
            iteration <= max(baseAmountOfIterations, distanceLeftQue.maxlen):
        lengthToGoX = abs(xCounter - oldXCounter - xDist)
        lengthToGoY = abs(yCounter - oldYCounter - yDist)
        sleep(0.004)
        # TODO Possible improvement: other distance metric
        distanceLeft = sqrt(pow(lengthToGoX, 2) + pow(lengthToGoY, 2))
        distanceLeftQue.append(distanceLeft)
        iteration += 1
    turnOffMotors()
    global currentPos
    # TODO Test: real value <-> expected value
    currentPos = measurePointCoordinate
    # # How much deviation is caused by the 3-step latency?
    print("circ buff: " + str(distanceLeftQue))
    # print("Current coor: " + str(currentPos))
    if distanceLeftQue[0] >= 50:
        print(" Wew, something went wrong there. Let's find out what!")
        print("  xSpeed: " + str(xSpeed) + " ySpeed: " + str(ySpeed))


def printQueue(vectorQueue):
    resetPos()
    # for vector in vectorQueue:
    vector = dummyVector
    # Move to starting position
    moveTo(numpyToEncoder(vector.pop(0)))
    # Start printing
    pumpOn()
    for coordinate in vector:
        moveTo(numpyToEncoder(coordinate))
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
In this project there are three axial systems:
  - the numpy coordinate system used by the slicer (320 x 320)
  - the encoder measuring system (1840 x 1760)
We below the converters (numpy, encoder) and (encoder, time)
The first is simple, the latter accommodates for ramping and inequality between motors
'''


def numpyToEncoder(numpyCoordinate):
    print("Numpy Coor: " + str(numpyCoordinate))
    x = numpyCoordinate[0]
    y = numpyCoordinate[1]
    # Slicer uses a grid system of 320 x 320
    x = x / 320.0
    y = y / 320.0
    x = x * maxMeasuringPointsXaxis
    y = y * maxMeasuringPointsYaxis
    return Coordinate(x, y)


# To avoid ramping of the dc motor we take the trajectory of a complete vector
#  and steer towards the end. At the end of a vector we stop completely
# def encoderToTime(encoderVector):
#     encoderVector.x


def test(vectorQueue):
    print("start test")
    # printQueue(vectorQueue)

    # resetPos()
    # moveTo(Coordinate(0, 0))
    # pumpOn()
    # drawRectangle(maxMeasuringPointsXaxis, maxMeasuringPointsYaxis)
    # moveTo(Coordinate(200, 200))
    # drawRectangle(maxMeasuringPointsXaxis / 2, maxMeasuringPointsYaxis)
    # pumpOff()

    printQueue([])


#    print(numpyToEncoder([160.0, 160.0]))
print("end")


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
