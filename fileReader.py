###
# Generates vectorarray examples given maximum x and y coordinates
# Vectors are continuously printed lines
###

from coordinates import Coordinate as Co

Co.default_order = 'xy'


class FileReader:
    def __init__(self, maxX: float, maxY: float):
        self.maxX = maxX
        self.maxY = maxY

    # Precondition: Starts in bottom left corner
    def rectangle(breadth, height):
        return [Co(0, 0),
                Co(breadth, 0),
                Co(breadth, height),
                Co(0, height),
                Co(0, 0)
                ]

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

    # Creeper face of Minecraft
    def creeper(self):
        # We use a resolution of 11x11
        res = 11.
        leftEye = [Co(3, 9), Co(4, 9), Co(4, 8), Co(3, 8)]
        rightEye = [Co(8, 9), Co(9, 9), Co(9, 8), Co(8, 8)]
        mouth = [Co(3, 3), Co(3, 6), Co(5, 6), Co(5, 7), Co(7, 7), Co(7, 6),
                 Co(9, 6), Co(9, 3), Co(8, 3), Co(8, 4), Co(4, 4), Co(4, 3)
                 ]
        total = [leftEye, rightEye, mouth]
        return self.scale(self.gridify(total, res, res))

    # Pokéball from Pokémon
    def pokeball(self):
        res = 10.
        outerBall = [Co(4, 1), Co(1, 4), Co(1, 7), Co(4, 10),
                     Co(7, 10), Co(10, 7), Co(10, 4), Co(7, 1), Co(4, 1)]
        innerBallTop = [Co(10, 5), Co(7, 5), Co(6, 7),
                        Co(5, 7), Co(4, 5), Co(1, 5)]
        innerBallBot = [Co(7, 5), Co(6, 4), Co(5, 4), Co(4, 5)]
        total = [outerBall, innerBallTop, innerBallBot]
        return self.scale(self.gridify(total, res, res))

    # A heartshape,
    def heart(self):
        res = 11.
        outerHeart = [Co(6, 1), Co(1, 6), Co(1, 9), Co(2, 10), Co(4, 10), Co(6, 8),
                      Co(8, 10), Co(10, 10), Co(11, 9), Co(11, 6), Co(6, 1)]
        innerHeart = [Co(6, 2), Co(2, 6), Co(2, 9), Co(4, 9), Co(6, 7),
                      Co(8, 9), Co(10, 9), Co(10, 6), Co(6, 2)]
        total = [outerHeart, innerHeart]
        return self.scale(self.gridify(total, res, res))

    # Parses one vector following the format: x1, y1 - x2, y2
    def parseVector(self, line):
        try:
            vector = []
            coordinates = line.strip().split('-')
            for coordinate in coordinates:
                x, y = coordinate.strip().split(',')
                parsedCo = Co(int(x), int(y))
                vector.append(parsedCo)
        except ValueError:
            print("Malformulated vectorline: " + line)
            print("We will print the figure without this vector")
        return vector

    # Parses files to printable lists of vectors
    # Lines that start with '#' are considered comments
    # The first line gives the x and y resolution
    # All following lines give one vector each
    def parse(self, filename):
        xRes, yRes = 0, 0
        totalVec = []
        with open(filename, 'r') as f:
            for line in f:
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
        return self.scale(self.gridify(totalVec, xRes, yRes))
