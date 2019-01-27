# NDL Pannenkoekenprinter report
Frank Gerlings, s4384873 - Januari 2019

This readme explains the structure of the code and the design decisions. For a list
 of all the necessary equipment and a user guide, see ``documentation > Pannenkoekenprinter 
Gebruikshandleiding.pdf``. These are seperated for the convenience of the people 
that use the project for open days.

## Motivation
The earlier printer had as main problem that it printed too slow. We tried to fix this with two modifications:
* Increase the flow by changing the hose
* Substituting the stepper motors by DC-motors with encoders

## Code structure
* ``./runme.py``: operates as TUI, is the main file of the project.
* ``./slicer/``: parses an images into vectors, lists of coordinates. The cod is from 
people that previously worked on the pannenkoekenprinter. I will use it as a library 
and will take no credit for this code.
* ``./drivers/``: ``dc_motor.py`` prints vectors. The rest of the folder is filled with 
files containing auxiliary classes.
* ``./documentation/``: contains more background information on this project, in 
particular ``Pannenkoekenprinter Gebruikshandleiding.pdf``.
* ``./images/``: contains all example images that the printer currently can print. 
More can be added, should the user feel the need to.

## Physical components
An overview can be found in [this spreadsheet](https://docs.google.com/spreadsheets/d/1BaNzUmYlQQ56a9a7txzUSEZhK_B5LRCAvkFlHnZ8L6Q/edit?usp=sharing). The first tab shows all parts currently used in the printer and possible new parts. The second tab shows the lay-out of the GPIO pins that have been used, how the encoders and the relais should be connected. The third tab shows the three ports of the relais.

## Memorisations
Scan for motor hat (I2C connections)
> sudo i2cdetect -y 1



Motoren volle bak aanzetten en daarna meten tot we niet dichterbij komen
# wanneer stoppen met bewegen:
#  - Fixed boundary (linear function)
#  -> Stop when not getting closer anymore
#    Skipt soms volledige beweging (-200,1400)
#  - Precalculate the estimated time

Python Geometry is traag. Doet meerdere seconden over intersection circle ray
moet eigenlijk in 0.003 seconden
Let's try Shapely, which is a wrapper of GEOS, based on C++ -> faster than Python
evaluate=false was ook niet snel genoeg 

TODO
Nog even symlinkje maken "pancake"
Create a requirements.txt (for Python)
autocomplete TUI
# Test all images, remove the ones that aren't sliced correctly
# Feature: tab completion for the images

# Libraries
Numpy
adafruit-circuitpython-motorkit
coordinates

