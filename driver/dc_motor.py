#! ../pyenv/bin/python3

import atexit
from math import sqrt, floor
import threading
from time import sleep
from coordinates import Coordinate

import RPi.GPIO as GPIO
from Adafruit_MotorHAT import Adafruit_MotorHAT

# Set variables
mh = Adafruit_MotorHAT(addr=0x70)

# The Pi is located at (0,0)
pos_x = 0
pos_y = 0

# Motor that goes over the x-axis, the motor itself is stationary
xMotor = mh.getMotor(1)
# Motor that goes over the y-axis, the motor itself is on the moving arm
yMotor = mh.getMotor(2)

GPIO.setmode(GPIO.BOARD)
GPIO.setup([7], GPIO.OUT)

def pumpOff():
   GPIO.cleanup()
   GPIO.output(7, GPIO.LOW)

def pumpOn():
   GPIO.cleanup()
   GPIO.output(7, GPIO.HIGH)

def turnOffMotors():
   xMotor.run(Adafruit_MotorHAT.RELEASE)
   yMotor.run(Adafruit_MotorHAT.RELEASE)

# Should the program on the Pi crash, the motors will be stopped
#  See motor hat documentation page 4
atexit.register(turnOffMotors)
atexit.register(pumpOff())

# There are two member functions:
# .setSpeed(X) with 0 < X < 255
# .run(direction)
#  with direction = Raspi_MotorHAT.FORWARD : forward
#  with direction = Raspi_MotorHAT.BACKWARD: backward
#  with direction = Raspi_MotorHAT.RELEASE : Stop

# Sets motor in position (0,0)
def resetPos():
    xMotor.run(Adafruit_MotorHAT.BACKWARD)
    for i in range(255):
        xMotor.setSpeed(i)
    yMotor.run(Adafruit_MotorHAT.BACKWARD)
    for i in range(170):
        yMotor.setSpeed(i)
    print("Start!")
    sleep(10)
    print("Reset to (0,0)")
    turnOffMotors()

def setDirection(motor, dist):
    if(dist>0):
        motor.run(Adafruit_MotorHAT.FORWARD)
    else:
        motor.run(Adafruit_MotorHAT.BACKWARD)

def drawLine(start, end):
    xDist = end.x - start.x
    yDist = end.y - start.y
    setDirection(xMotor, xDist)
    setDirection(yMotor, yDist)

    # Now set length
    xDist = abs(xDist)
    yDist = abs(yDist)
    if(xDist == 0):
      xMotor.setSpeed(0)
      for i in range(255):
          yMotor.setSpeed(i)
    else:
        speedDif = yDist/xDist
        for i in range(255):
                if(xDist > yDist):
                    xMotor.setSpeed(255)
                    yMotor.setSpeed(floor(255*speedDif))
                else:
                    xMotor.setSpeed(floor(255/speedDif))
                    yMotor.setSpeed(255)
    length = sqrt(xDist*xDist + yDist*yDist)
    # The total drawing zone is traversed in 5 seconds
    sleep(length/2)

# Precondition: Starts in bottomleft corner
def drawRectangle(length, breadth):
    drawLine(Coordinate(x=0,y=0), Coordinate(x=length,y=0))
    drawLine(Coordinate(x=length,y=0), Coordinate(x=length,y=breadth))
    drawLine(Coordinate(x=length,y=breadth), Coordinate(x=0,y=breadth))
    drawLine(Coordinate(x=0,y=breadth), Coordinate(x=0,y=0))

def niceFigure():
    drawRectangle(10,10)
    drawLine(Coordinate(x=2.5,y=2.5))
    drawLine(Coordinate(x=7.5,y=2.5))
    drawLine(Coordinate(x=10,y=0))
    # pompje uit
    drawLine(Coordinate(x=7.5,y=2.5))
    # pompje aan
    drawLine(Coordinate(x=7.5,y=7.5))
    drawLine(Coordinate(x=10,y=10))
    # pompje uit
    drawLine(Coordinate(x=7.5,y=7.5))
    # pompje aan
    drawLine(Coordinate(x=2.5,y=7.5))
    drawLine(Coordinate(x=0,y=10))
    # uit
    drawLine(Coordinate(x=2.5,y=7.5))
    # aan
    drawLine(Coordinate(x=2.5,y=7.5))
    # uit
    drawLine(Coordinate(x=0,y=0))

def printVector(vector):
    print(vector)

def print(vectorQueue):
    print("Starting placeholder printing")
    for vector in vectorQueue:
	printVector(vector)

#pumpOn()
#print("pump on")
#sleep(0.2)
#pumpOff()
#print("pump off")

drawRectangle(5,5)

#    calibration_length = 0;
#    while (True):
#        print("Length: " + str(calibration_length))
#        if (raw_input("Continue?") == "N"):
#            break;
#        calibration_length = calibration_length + 200
#        myDC.step(200, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.SINGLE)

#    while (True):
#        print("Length: " + str(calibration_length))
#        if (raw_input("Continue?") == "N"):
#            break;
#        calibration_length = calibration_length + 20
#        myDC.step(20, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.SINGLE)

#    print("Final calibrated length: " + str(calibration_length))
#    return calibration_length

#GPIO.cleanup(7)
#def stepper_worker(myDC, distance, speed):
#    myDC.setSpeed(int(speed))
#    if (distance > 0):
#        myDC.step(distance, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.SINGLE)
#    else:
#        if (distance < 0):
#            myDC.step(abs(distance), Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.SINGLE)


#def move(x, y, speed):
#    x = int(x/1)
#    y = int(y/-1)
#    global pos_x, pos_y
#    # max_distance = math.sqrt(1.0 * x * x + y * y)
#    x = x - pos_x
#    y = y - pos_y
#    pos_x = pos_x + x;
#    pos_y = pos_y + y;

    # if (x != 0):
    #    st1 = threading.Thread(target=stepper_worker, args=(myDC1, x, max(0, 30.0 * (abs(x)/max_distance))))
    # if (y != 0):
    #    st2 = threading.Thread(target=stepper_worker, args=(myDC2, y, max(0, -3.0 + 24.0 * (abs(y)/max_distance))))

#    if (x != 0):
#        st1 = threading.Thread(target=stepper_worker, args=(myDC1, x, speed))
#    if (y != 0):
#        st2 = threading.Thread(target=stepper_worker, args=(myDC2, y, speed))#

#    if (x != 0):
#        st1.start()
#    if (y != 0):
#        st2.start()

#    if (x != 0):
#        st1.join()
#    if (y != 0):
#        st2.join()

#used_set = instruction_dictionary['kill_me']

#def move_vector(vector):
#    for next_instruction in vector:
#        move(next_instruction[0]+10, next_instruction[1]+10, run_motorspeed)

#def print_vector(vector):
#    init_pos = vector[0]
#    move(init_pos[0]+10, init_pos[1]+10, run_motorspeed)
#    print("beslag aan!")
#    GPIO.setup([7], GPIO.OUT)
#    GPIO.output(7, 1)
#    sleep(.2)
#    for next_instruction in vector[1:]:
#        move(next_instruction[0]+10, next_instruction[1]+10, run_motorspeed)
#    print("beslag uit!")
#    GPIO.cleanup(7)
#    sleep(.2)

#def flush_the_tube():
#    GPIO.setup([7], GPIO.OUT)
#    GPIO.output(7, 1)
#    sleep(60)
#    GPIO.cleanup(7)
#    sleep(.2)
