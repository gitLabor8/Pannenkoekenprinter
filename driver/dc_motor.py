#! ../pyenv/bin/python3

import atexit
from math import sqrt, floor
from time import sleep
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
    xMotor.run(Adafruit_MotorHAT.RELEASE)
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
    moveTo(Coordinate(0, 400))
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
    motor.setSpeed(speed)
    # Ramping method (better for motor condition?)
    # for i in range(speed):
    #     motor.setSpeed(i)


# Takes end point in measuring points
# Moves the head without printing
def moveTo(measurePointCoordinate):
    xDist = measurePointCoordinate.x - currentPos.x
    yDist = measurePointCoordinate.y - currentPos.y
    setDirection(xMotor, xDist)
    setDirection(yMotor, yDist)
    print("xdist, ydist = " + str(xDist) + " " + str(yDist))

    # Now we set the length
    xDist = abs(xDist)
    yDist = abs(yDist)
    # The Y-motor is about 4% faster than the X-motor, see statistics in spreadsheet
    speedDif = maxTimeXaxis / maxTimeYaxis

    if (xDist == 0):
        revUpMotor(yMotor, maxSpeed)
    else:
        distDif = yDist / xDist
        if (xDist > yDist):
            revUpMotor(xMotor, floor(maxSpeed))
            revUpMotor(yMotor, floor(maxSpeed * distDif / speedDif))
        else:
            revUpMotor(xMotor, floor(maxSpeed / distDif))
            revUpMotor(yMotor, floor(maxSpeed / speedDif))

    # Roll until we are almost there
    oldXCounter, oldYCounter = xCounter, yCounter
    lengthToGoX = abs(xCounter - oldXCounter - xDist)
    lengthToGoY = abs(yCounter - oldYCounter - yDist)
    while not lengthToGoX + lengthToGoY < 4:
        sleep(0.002)
        # Debug string to check the difference between x and y
        if lengthToGoX < 5 or lengthToGoY < 5:
            print("lengthToGoX: " + str(lengthToGoX))
            print("lengthToGoY: " + str(lengthToGoY))
            print(str(yCounter) + " " +str(oldYCounter) + " " +str(yDist))


def printQueue(vectorQueue):
    print("Starting placeholder printing")
    for vector in vectorQueue:
        moveTo(numpyToEncoder(vector[0]))
        pumpOn()
        for coordinate in vector:
            moveTo(numpyToEncoder(coordinate))
        pumpOff()


# Precondition: Starts in bottom left corner
def drawRectangle(breadth, height):
    moveTo(Coordinate(0, height))
    sleep(10)
    moveTo(Coordinate(breadth, height))
    sleep(10)
    moveTo(Coordinate(breadth, 0))
    sleep(2)
    moveTo(Coordinate(0, 0))


'''
##
# Axial systems
##
In this project there are three axial systems:
  - the numpy coordinate system used by the slicer (320 x 320)
  - the encoder measuring system (1840 x 1760)
  - the time for the motors at full speed to reach a point in seconds(5 x 6)
We below the converters (numpy, encoder) and (encoder, time)
The first is simple, the latter accommodates for ramping and inequality between motors
'''


def numpyToEncoder(numpyCoordinate):
    print("Next coor: " + str(numpyCoordinate))
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


    resetPos()
#    drawRectangle(maxMeasuringPointsXaxis, maxMeasuringPointsYaxis/2)

    # printQueue(vectorQueue)

    #    print(numpyToEncoder([160.0, 160.0]))
    print("end")


# Flushes the tube for 60 seconds (for cleaning)
def flushTube():
    pumpOn()
    sleep(60)
    pumpOff()
