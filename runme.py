###
# Main file of the project. Presents the user a TUI and handles the input
###

from drivers import dc_motor as driver
from fileReader import FileReader
from drivers import pump
from os import walk

fr = FileReader(driver.maxMeasuringPointsXaxis, driver.maxMeasuringPointsYaxis)


def programSelector():
    print("Please enter the name of the file that you would like to print or "
          "the command that you would like to use. \n"
          "Some examples: \n"
          " + \"pan calibrate\" to draw a rectangle showing the reach "
          "of the printer. Useful when you want to know if you've placed the pan "
          "correctly\n"
          " + \"flush tube\" to flush the tube. Useful when you're done printing "
          "and want to Clean the tube with hot water. Default: 10 minutes\n"
          " + \"list\" to show all possible prints\n"
          " + finally, to exit prematurely press \"ctrl + c\"")
    command = input("Please type the image name/command here: ")
    print("")
    if command == "pan calibrate":
        driver.drawingRange()
    elif command == "flush tube":
        pump.flushTube()
    elif command == "list":
        # Crawl the examples folder
        for root, dirs, files in walk("./examples/"):
            for filename in files:
                print(filename)
        print("Type the filename to print it")
    else:
        try:
            with open(command, 'r') as file:
                vectorArray = fr.parse(file)
                driver.printVectorArray(vectorArray)
        except OSError:
            print("> I didn't quite get that, please format your choice correctly\n")
            programSelector()
        else:
            print("> I didn't quite get that, please format your choice "
                  "correctly\n")
            programSelector()


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
        pump.off()
        driver.resetPos()
        print("Call me up again by typing \"python3 "
              "/home/pi/Desktop/Pannenkoekenprinter/runme.py\" or \"pancake\"")


main()
