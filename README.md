# Pannenkoekenprinter
This readme explains the structure of the code and the design decisions. For a list
 of all the necessary equipment and a user guide, see ``documentation > Pannenkoekenprinter 
Gebruikshandleiding.pdf``.

## File/code structure

## Physical components
An overview can be found in [this spreadsheet](https://docs.google.com/spreadsheets/d/1BaNzUmYlQQ56a9a7txzUSEZhK_B5LRCAvkFlHnZ8L6Q/edit?usp=sharing). The first tab shows all parts currently used in the printer and possible new parts. The second tab shows the lay-out of the GPIO pins that have been used, how the encoders and the relais should be connected. The third tab shows the three ports of the relais.

## Motivation
The earlier printer had as main problem that it printed too slow. We tried to fix this with two modifications:
* Increase the flow by changing the hose
* Substituting the stepper motors by DC-motors with encoders
Since the first isn't that technical, we will now go into detail on how we did the latter.

## Memorisations
Scan for motor hat (I2C connections)
> sudo i2cdetect -y 1

\title{NDL Pannenkoekenprinter rapport}
\author{Frank Gerlings, s4384873}
\date{Januari 2019}

\begin{document}

\maketitle

Motoren volle bak aanzetten en daarna meten tot we niet dichterbij komen
# wanneer stoppen met bewegen:
#  - Fixed boundary (linear function)
#  -> Stop when not getting closer anymore
#    Skipt soms volledige beweging (-200,1400)
#  - Precalculate the estimated time

Python Geometry is traag. Doet meerdere seconden over intersection circle ray
moet eigenlijk in 0.003 seconden
Let's try Shapely, which is a wrapper of GEOS, based on C++ -> faster than Python

TODO
Nog even symlinkje maken "pancake"
Create a requirements.txt (for Python)
# Test all images, remove the ones that aren't sliced correctly
# Feature: tab completion for the images

\end{document}

