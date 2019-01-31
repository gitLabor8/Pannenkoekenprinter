###
# Generates vectorarray examples given maximum x and y coordinates
# Vectors are continuously printed lines
###

import coordinates.Coordinate as Co

Co.default_order = 'xy'


class Examples:
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

    # Creeper face of Minecraft
    def creeper(self):
        # We use a resolution of 11x11
        res = 11.
        leftEye = [Co(3, 9), Co(4, 9), Co(4, 8), Co(3, 8)]
        rightEye = [Co(8, 9), Co(9, 9), Co(9, 8), Co(8, 8)]
        mouth = [Co(3, 3), Co(3, 6), Co(5, 6), Co(5, 7), Co(7, 7), Co(7, 6),
                 Co(9, 6), Co(9, 3), Co(8, 3), Co(8, 4), Co(4, 4), Co(4, 3)
                 ]
        mouthFill = [Co(5, 5), Co(7, 5)]
        total = [leftEye, rightEye, mouth, mouthFill]
        return self.scale(self.gridify(total))
