###
# Reads files and converts them to printable vector arrays
# A vectors is a continuously printed line
###

from coordinates import Coordinate as Co

Co.default_order = 'xy'


class FileReader:
    def __init__(self, maxX: float, maxY: float):
        self.maxX = maxX
        self.maxY = maxY

    # Scale an image
    def scale(self, vectorArray: [float]):
        for vector in vectorArray:
            for coordinate in vector:
                coordinate.x *= self.maxX
                coordinate.y *= self.maxY
        return vectorArray

    # Converts local coordinates into percentage places in a grid
    def gridify(self, vectorArray: [float], resX: float, resY: float):
        for vector in vectorArray:
            for coordinate in vector:
                coordinate.x = coordinate.x / resX
                coordinate.y = coordinate.y / resY
        return vectorArray

    # Parses one vector following the format: x1, y1 - x2, y2
    def parseVector(self, line):
        vector = []
        coordinates = line.strip().split('-')
        for coordinate in coordinates:
            x, y = coordinate.strip().split(',')
            parsedCo = Co(int(x), int(y))
            vector.append(parsedCo)
        return vector

    # Parses files to printable lists of vectors
    # Lines that start with '#' are considered comments
    # The first line gives the x and y resolution
    # All following lines give one vector each
    def parse(self, file):
        xRes, yRes = 0, 0
        totalVec = []
        for line in file:
            try:
                line = line.strip()
                # Neglect comments
                if not line.startswith("#"):
                    # Catch the resolutions
                    if xRes == 0 and yRes == 0:
                        xRes, yRes = line.strip().split(',')
                        xRes, yRes = int(xRes.strip()), int(xRes.strip())
                    # Parse a vector
                    else:
                        totalVec.append(self.parseVector(line))
            except ValueError:
                print("Malformulated vectorline: " + line)
                print("We will print the figure without this vector")

        return self.scale(self.gridify(totalVec, xRes, yRes))
