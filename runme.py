###
# Main file of the project. Presents the user a TUI and handles the input
###

from drivers import dc_motor as driver
from examples import Examples
from drivers import pump

ex = Examples(driver.maxMeasuringPointsXaxis, driver.maxMeasuringPointsYaxis)


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
    imageName = input("Please type the image name/command here: ")
    print("")
    if imageName == "pan calibrate":
        driver.drawingRange()
    elif imageName == "flush tube":
        pump.flushTube()
    elif imageName == "list":
        print("- \"heart\": A nice heart shape\n"
              "- \"creeper\": A creepy face from the depths of Minecraft\n"
              "- \"pokeball\": Pokéball for catching Snorelax!\n"
              " Type the name to print it"
              )
    else:
        if imageName == "heart":
            driver.printVectorArray(ex.heart())
        elif imageName == "creeper":
            driver.printVectorArray(ex.creeper())
        elif imageName == "pokeball":
            driver.printVectorArray(ex.pokeball())
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
