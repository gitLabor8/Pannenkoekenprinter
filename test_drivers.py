###
# Gives outprints of error-prone (mathematical) functions
###

from drivers.dc_motor import *

''''
###
# dc_motor.py
###
'''


# Speedmodifier should scale up from 0.8 to 1.0 where 0.9 is used as default
# speed, higher is used to compensate for being to slow and lower to compensate
# for being to quick
def testSpeedModifier():
    # i is our relative position e.g. -30 is below the point, so it should have a
    # modifier somewhere in ]0.9, 1.0]
    # When going in the positive direction
    for i in range(-36, 36, 1):
        mod = speedModifier(i, 0, True)
        print("At relative position: " + str(i) + ", mod: " + str(mod))
    # When going in the negative direction
    for i in range(-36, 36, 1):
        mod = speedModifier(i, 0, False)
        print("At relative position: " + str(i) + ", mod: " + str(mod))


# SpeedNearEnd should slow down in from maxSpeed to minSpeed in the last 200 steps
# It should print a descending list
def testSpeedNearEnd():
    for i in range(205, 0, -1):
        speed = speedNearEnd(i)
        print("At distance: " + str(i) + ", speed: " + str(speed))


''''
###
# path.py
###
'''


def testExpectedPos(path: Path):
    print(str(path))
    distLeftList = [path.totalDist / 10 * x for x in range(0, 11)]
    for distLeft in distLeftList:
        expectedPos = path.expectedPos(distLeft)
        print(" at distance " + str(distLeft) + " is coordinate: "
              + str(expectedPos))


def testMultipleExpectedPos():
    horizontalAscending = Path(Coordinate(0, 0), Coordinate(100, 0))
    testExpectedPos(horizontalAscending)
    horizontalDescending = Path(Coordinate(100, 0), Coordinate(0, 0))
    testExpectedPos(horizontalDescending)
    verticalAscending = Path(Coordinate(0, 0), Coordinate(0, 100))
    testExpectedPos(verticalAscending)
    verticalDescending = Path(Coordinate(0, 100), Coordinate(0, 0))
    testExpectedPos(verticalDescending)
    diagonalAscending = Path(Coordinate(0, 0), Coordinate(100, 100))
    testExpectedPos(diagonalAscending)
    diagonalDescending = Path(Coordinate(100, 100), Coordinate(0, 0))
    testExpectedPos(diagonalDescending)


''''
###
# dc_motor_adafruit_wrapper.py
###
'''


# Test if the mathematical side of speedUp is up to speed ;-)
# Should not allow the motor to directly speed up a lot, since that would make the
#  program temporarily insensitive to changes
def testSpeedUp():
    # Stationary motor, responsible for x-axis
    motor = MotorWrapper(1)
    # Let it move forward
    motor.setDirection(1)

    print("Directly ask for the maxSpeed")
    for i in range(0, maxSpeed, 10):
        motor.speedUp(maxSpeed)
        print(" Calculated speed: " + str(motor.speed))

    print("Directly ask for a stop")
    for i in range(0, maxSpeed, 10):
        motor.speedUp(0)
        print(" Calculated speed: " + str(motor.speed))

    sleep(1)

    print("Slow ramp: he should be able to keep up with this")
    for i in range(0, maxSpeed + 10, 10):
        motor.speedUp(i)
        print(" Calculated speed: " + str(motor.speed))

    print("Slow descent: he should be able to keep up with this")
    for i in range(maxSpeed, -10, -10):
        motor.speedUp(i)
        print(" Calculated speed: " + str(motor.speed))
