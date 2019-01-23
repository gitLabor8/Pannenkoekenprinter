###
# Calculates a path given it's begin and end points. Can give expected positions
#  when given a percentage
###

from numpy import sqrt
from coordinates import Coordinate

Coordinate.default_order = 'xy'


class Path:
    def __init__(self, begin: Coordinate, end: Coordinate):
        self.begin = begin
        self.end = end
        self.xDist = end.x - begin.x
        self.yDist = end.y - begin.y
        self.totalDist = sqrt(pow(self.xDist, 2) + pow(self.yDist, 2))
        # self.slope = distanceLeftY/distanceLeftX
        print("xdist, ydist = " + str(self.xDist) + " " + str(self.yDist))

    # Precondition: we haven't passed the end point yet
    def expectedPos(self, distanceLeft: float):
        percentage = 1 - distanceLeft / self.totalDist
        xCoor = percentage * self.xDist
        yCoor = percentage * self.yDist
        return Coordinate(xCoor, yCoor)
