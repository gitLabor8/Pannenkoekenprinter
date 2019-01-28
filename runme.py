from slicer import slice_run as slicer
from PIL import Image
from drivers import dc_motor as driver
from drivers import pump
from os import walk


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
        pump.flushTube()
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
    driver.printVectorQueue(vectorQueue)


def main():
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


# # Just some quick testing
printPancake(Image.open("images/ghostbloc.jpg"))
# driver.resetPos()
# driver.test([])
# main()


# Hij wordt onnauwkeurig doordat:
# - hij 2% afwijking heeft op de y-meetwaarden en 0,8% op de x-as
#  -> Reset na x aantal meetpunten
# - hij standaard voorbij zijn dichtst bijzijnde punt afrijdt
# - een gekke bug waardoor hij 50 naast zijn waarde zit
# - de motoren zijn wonky (zeker die op de y-as) -> wielen veranderen
# - hij print heel dik -> klemmetje
# - ik kan ze maar aan een kant bakken -> hij moet rustig bakken
# Sinful: - Total dist bijhouden en iedere x keer resetPos?
# - mist misschien interrupts? "measuring callback GPIO"

# Hoe meet ik hoe lang hij aan het rekenen is op de body in mijn loop?
# Naming universally consistent xSpeed <-> speedX
# Rewrite geometry library
