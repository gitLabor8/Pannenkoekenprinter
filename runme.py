import slicer.slice_run as slicer
from PIL import Image
import driver.dc_motor as driver
from os import walk

###
# Vraagjes aan Pieter
###
# x-as motor 'wonky' door asymmetrische as
# User interface: kiezen tussen afbeeldingen, resetPos, flushing en outline
#  hoe uitgebreid precies? TUI? SYMLINKje is wel chill
# Why dc motor in for-loop?
# Pump not centered: ty-rap broke
# Split into multiple files? 300+ lines of code/comment. Pump <-> motor
# wanneer stoppen met bewegen:
#  - Fixed boundary (linear function)
#  -> Stop when not getting closer anymore
#    Skipt soms volledige beweging (-200,1400)
#  - Precalculate the estimated time
#  -> wil je dit in het verslag hebben?
# Experimenteren met beslag:
#  - coordinaat updaten naar werkelijke waarde
#  - coordinaat updaten naar verwachtte waarde
# Vertragen naar mate we dichter bij het einde komen is een no-go. Op iedere hoek
# zouden we dan trager gaan, waardoor er dikkere klodders ontstaan: de pomp is
# namelijk op volle toeren doorgaan# vectorQueue is a deque of vectors
# # a vector is a numpy.ndarray of coordinates
# # a coordinate is an 1x2 array of floats 0.0 <= x <= 320
# Test all images, remove the ones that aren't sliced correctly
# Feature: tab completion for the images

def programSelector():
    print("Please enter the name of the file that you would like to print or "
          "the command that you would like to use. \n"
          "Some examples: \n"
          " + \"pan calibrate\" to draw a rectangle showing the reach "
          "of the printer. Useful when you want to know if you've placed the pan "
          "correctly\n"
          " + \"flush tube\" to flush the tube. Useful when you're done printing "
          "and want to Clean the tube with hot water\n"
          " + \"heart.png\" to print \\images\\heart.png\n"
          " + \"list\" to show all other possible images\n"
          " + finally, to exit press \"ctrl + c\"")
    imageName = input("Please type the image name/command here: ")
    print("")
    if imageName == "pan calibrate":
        driver.drawingRange()
    elif imageName == "flush tube":
        driver.flushTube()
    # Crawl the images folder for all files
    elif imageName == "list":
        for root, dirs, files in walk("./images/"):
            for filename in files:
                print(filename)
    else:
        try:
            image = Image.open("images/" + imageName)
            printPancake(image)
        except OSError:
            print("> I didn't quite get that, please format your choice correctly\n")
            programSelector()


def printPancake(image):
    gray = image.convert("L")
    bw = gray.point(lambda x: 0 if x < 128 else 255, '1')
    print("Starting slicing")
    vectorQueue = slicer.Slice_Image(bw, SQRSIZE=400, BLURRED=True, EQUALIZED=False, \
                                     CWHITE=False, INVERTED=False, RETURN_IMG=False,
                                     SINGLE=False, BOT=True, MID=True, TOP=True)
    print("Finished slicing")
    print("Starting printing")
    driver.test(vectorQueue)


try:
    print("Hello! Welcome to the Pannenkoekenprinter.\n")
    while True:
        programSelector()
        print("Done!\n"
              "How about another pancake?\n")
except KeyboardInterrupt:
    print("\n\nWant to quit printing already?\n"
          "Let me get out of the way, gimme a sec")
    driver.resetPos()
    print("Call me up again by typing \"python3 runme.py\"")
