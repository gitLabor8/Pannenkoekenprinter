###
# Wraps around the Adafruit motor and supplies some more functions
# Prevents duplicate code for the x and y motor separately
#
# If we want the motors to respond, we need to slowly ramp them up. This leads to
# function calls taking a lot of time. speedUp tries to deal with this.
###

from numpy import floor
from Adafruit_MotorHAT import Adafruit_MotorHAT
import atexit

mh = Adafruit_MotorHAT(addr=0x70)
maxSpeed = 255


class MotorWrapper:
    def __init__(self, number: int):
        # Options for number:
        # 1: Motor that goes over the x-axis, the motor itself is stationary
        # 2: Motor that goes over the y-axis, the motor itself is on the moving arm
        if number == 1 or number == 2:
            self.motor = mh.getMotor(number)
        else:
            print("MotorWrapper init: number is wrong: " + str(number))
        self.speed = 0

        # Should the program on the Pi crash, the motors must be stopped explicitly
        #  See motor hat documentation page 4
        atexit.register(self.turnOff)

    def turnOff(self):
        self.setSpeed(0)
        self.motor.run(Adafruit_MotorHAT.RELEASE)

    def setDirection(self, dist: float):
        if (dist > 0):
            self.motor.run(Adafruit_MotorHAT.FORWARD)
        else:
            self.run(Adafruit_MotorHAT.BACKWARD)

    # On purpose named after the original MotorHAT function
    def run(self, direction):
        self.motor.run(direction)

    # Does not care about running time, slowly ramps up to speed
    # On purpose named after the original MotorHAT function
    def setSpeed(self, speed: float):
        speed = self.speedCheck(speed)
        for i in range(speed):
            self.motor.setSpeed(i)

    # Ramping may not take long, so prematurely stop it should it be to big
    # Returns the speed at which it stopped it's ramp
    def speedUp(self, speedNew: float):
        speedNew = self.speedCheck(speedNew)
        speedDif = speedNew - self.speed
        # Maximum accelleration in one cycle. Lower to poll more often
        maxAccInOneCycle = 12
        if speedDif > 0:
            if speedDif > maxAccInOneCycle:
                upperbound = self.speed + maxAccInOneCycle
            else:
                upperbound = self.speed + speedDif
            for i in range(self.speed, upperbound):
                self.motor.setSpeed(i)
            self.speed = upperbound
            if speedNew > maxSpeed:
                print("wrong! " + str(upperbound) + " " + str(speedNew))
            return upperbound
        else:
            if abs(speedDif) < maxAccInOneCycle:
                lowerbound = self.speed + speedDif
            else:
                lowerbound = self.speed - maxAccInOneCycle
            for i in range(self.speed, lowerbound, -1):
                self.motor.setSpeed(i)
            self.speed = lowerbound
            if lowerbound > maxSpeed:
                print("wrong! " + str(lowerbound) + " " + str(speedNew))
            return lowerbound

    # Error messaging & correction
    def speedCheck(self, speed: float):
        speed = int(floor(speed))
        if speed > 255:
            print("Speed is higher than 255/max: " + str(speed))
            print(" Using maxSpeed to proceed")
            return 255
        if speed < 0:
            print("Speed is negative: " + str(speed))
            print(" Using 0 to proceed")
            return 0
        return speed
