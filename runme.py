import slicer.slice_run as slicer
from PIL import Image
import driver.dc_motor as driver
import RPi.GPIO as GPIO

###
# Vraagjes aan Pieter
###
# x-as motor 'wonky' door asymmetrische as
# User interface: kiezen tussen afbeeldingen, resetPos en flushing
#  hoe uitgebreid precies? TUI?
#  anti-switch bouncing

# Prepend a # on the next line to switch between slicer and driver
'''
imgname = "images/flag.png"
picture = Image.open(imgname).convert("L")
gray = picture.convert('L')
bw = gray.point(lambda x: 0 if x < 128 else 255, '1')
print("Starting Slicing")
vectorQueue = slicer.Slice_Image(bw, SQRSIZE=400, BLURRED=True, EQUALIZED=False, \
                                 CWHITE=False, INVERTED=False, RETURN_IMG=False, SINGLE=False, \
                                 BOT=True, MID=True, TOP=True)
# vectorQueue is a deque of vectors
# a vector is a numpy.ndarray of coordinates
# a coordinate is an 1x2 array of floats 0.0 <= x <= 320
print(str(vectorQueue.pop()[0]))
'''
try:
    # driver.printQueue(vectorQueue)
    driver.resetPos()
except KeyboardInterrupt:
    print("Manual exit: ctrl + c")

finally:
    GPIO.cleanup()
    driver.turnOffMotors()
# '''
#
# import matplotlib.pyplot as plt
# # #
# imgname = "images/eiffeltower.png"
# picture = Image.open(imgname).convert("L")
# #
# plt.imshow(Image.open(imgname))
# plt.show()
# #
# slicer.Slice_Image(picture, SQRSIZE=500, BLURRED=True, EQUALIZED=False,\
#  CWHITE=False, INVERTED=False, RETURN_IMG=False, SINGLE=True,\
#   BOT=False, MID=True, TOP=False)
#
# imgname = "images/rtilted.jpg"
# picture = Image.open(imgname).convert("L")
# slicer.Slice_Image(picture, SQRSIZE=500, BLURRED=True, EQUALIZED=False,\
#  CWHITE=True, INVERTED=False, RETURN_IMG=False, SINGLE=True,\
#   BOT=True, MID=False, TOP=False)

# imgname = "images/rcenter.jpg"
# picture = Image.open(imgname).convert("L")
# slicer.Slice_Image(picture, SQRSIZE=500, BLURRED=True, EQUALIZED=False,\
#  CWHITE=False, INVERTED=False, RETURN_IMG=False, SINGLE=True,\
#   BOT=True, MID=False, TOP=False)
#
# imgname = "images/derpyheart_2.png"
# picture = Image.open(imgname).convert("L")
# slicer.Slice_Image(picture, SQRSIZE=500, BLURRED=False, EQUALIZED=False, CWHITE=True, INVERTED=False, RETURN_IMG=False, SINGLE=True, BOT=True, MID=False, TOP=False)

#
# imgname = "images/radboud.png"
# picture = Image.open(imgname).convert("L")
# slicer.Slice_Image(picture, SQRSIZE=110, BLURRED=False, EQUALIZED=False, CWHITE=False, INVERTED=False, RETURN_IMG=False, SINGLE=True)
