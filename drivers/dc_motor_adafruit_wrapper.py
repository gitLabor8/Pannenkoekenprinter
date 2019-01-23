###
# Wraps around the Adafruit motor and supplies some more functions
# Prevents duplicate code for the x and y motor seperatly
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

        self.motor = mh.getMotor(number)
        self.speed = 0

        # Should the program on the Pi crash, the motors will be stopped
        #  See motor hat documentation page 4
        atexit.register(self.turnOff)

    def turnOff(self):
        self.setSpeed(0)
        self.motor.run(Adafruit_MotorHAT.RELEASE)

    def setDirection(self, dist):
        if (dist > 0):
            self.motor.run(Adafruit_MotorHAT.FORWARD)
        else:
            self.run(Adafruit_MotorHAT.BACKWARD)

    # On purpose named after the original MotorHAT function
    def run(self, direction):
        self.motor.run(direction)

    # Does not care about running time, slowly ramp up to speed
    # On purpose named after the original MotorHAT function
    def setSpeed(self, speed: float):
        speed = self.speedCheck(speed)
        for i in range(speed):
            self.motor.setSpeed(i)

    # Does care about running time
    # Returns the speed at which it is actually running
    def speedUp(self, speedNew):
        speedNew = self.speedCheck(speedNew)
        # accelerating
        # TODO Git commit once it works-ish
        acceleration = speedNew - self.speed
        # Ramping cannot take long, so prematurely stop it should it be to big
        maxAccInOneCycle = 12
        if acceleration > 0:
            if acceleration > maxAccInOneCycle:
                upperbound = self.speed + maxAccInOneCycle
            else:
                upperbound = self.speed + acceleration
            for i in range(self.speed, upperbound):
                # print("amping to " + str(i))
                self.motor.setSpeed(i)
            self.speed = upperbound
            return upperbound
        else:
            if acceleration < -maxAccInOneCycle:
                lowerbound = self.speed - maxAccInOneCycle
            else:
                lowerbound = self.speed = acceleration
            for i in range(self.speed, lowerbound, -1):
                self.motor.setSpeed(i)
            self.speed = lowerbound
            return lowerbound

    # Error messaging & correction
    def speedCheck(self, speed):
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
