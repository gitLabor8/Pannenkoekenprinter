import atexit
import math
import threading
from time import sleep

import RPi.GPIO as GPIO
from Adafruit_MotorHAT import Adafruit_MotorHAT

# Set variables
mh = Adafruit_MotorHAT(addr=0x6F)
pos_x = 0
pos_y = 0
GPIO.setmode(GPIO.BOARD)
GPIO.setup([7], GPIO.OUT)

run_motorspeed = 30


def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

# Should the program on the Pi crash, the motors will be stopped
#  See motor hat documentation page 4
atexit.register(turnOffMotors)

# There are two member functions:
# .setSpeed(X) with 0 < X < 255
# .run(direction)
#  with direction = Raspi_MotorHAT.FORWARD : forward
#  with direction = Raspi_MotorHAT.BACKWARD: backward
#  with direction = Raspi_MotorHAT.RELEASE : Stop

def calibrate(myDC):
    myDC.setSpeed(20)
    calibration_length = 0;
    while (True):
        print("Length: " + str(calibration_length))
        if (raw_input("Continue?") == "N"):
            break;
        calibration_length = calibration_length + 200
        myDC.step(200, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.SINGLE)

    while (True):
        print("Length: " + str(calibration_length))
        if (raw_input("Continue?") == "N"):
            break;
        calibration_length = calibration_length + 20
        myDC.step(20, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.SINGLE)

    print("Final calibrated length: " + str(calibration_length))
    return calibration_length

myDC1 = mh.getStepper(1)  # motor port #1            # 40 RPM
myDC2 = mh.getStepper(2)  # motor port #1            # 40 RPM
GPIO.cleanup(7)
def stepper_worker(myDC, distance, speed):
    myDC.setSpeed(int(speed))
    if (distance > 0):
        myDC.step(distance, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.SINGLE)
    else:
        if (distance < 0):
            myDC.step(abs(distance), Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.SINGLE)


def move(x, y, speed):
    x = int(x/1)
    y = int(y/-1)
    global pos_x, pos_y
    # max_distance = math.sqrt(1.0 * x * x + y * y)
    x = x - pos_x
    y = y - pos_y
    pos_x = pos_x + x;
    pos_y = pos_y + y;

    # if (x != 0):
    #    st1 = threading.Thread(target=stepper_worker, args=(myDC1, x, max(0, 30.0 * (abs(x)/max_distance))))
    # if (y != 0):
    #    st2 = threading.Thread(target=stepper_worker, args=(myDC2, y, max(0, -3.0 + 24.0 * (abs(y)/max_distance))))

    if (x != 0):
        st1 = threading.Thread(target=stepper_worker, args=(myDC1, x, speed))
    if (y != 0):
        st2 = threading.Thread(target=stepper_worker, args=(myDC2, y, speed))

    if (x != 0):
        st1.start()
    if (y != 0):
        st2.start()

    if (x != 0):
        st1.join()
    if (y != 0):
        st2.join()

#used_set = instruction_dictionary['kill_me']

def move_vector(vector):
    for next_instruction in vector:
        move(next_instruction[0]+10, next_instruction[1]+10, run_motorspeed)

def print_vector(vector):
    init_pos = vector[0]
    move(init_pos[0]+10, init_pos[1]+10, run_motorspeed)
    print("beslag aan!")
    GPIO.setup([7], GPIO.OUT)
    GPIO.output(7, 1)
    sleep(.2)
    for next_instruction in vector[1:]:
        move(next_instruction[0]+10, next_instruction[1]+10, run_motorspeed)
    print("beslag uit!")
    GPIO.cleanup(7)
    sleep(.2)

def flush_the_tube():
    GPIO.setup([7], GPIO.OUT)
    GPIO.output(7, 1)
    sleep(60)
    GPIO.cleanup(7)
    sleep(.2)
