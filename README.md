# Pannenkoekenprinter
## File/code structure

## Physical components
An overview can be found in [this spreadsheet](https://docs.google.com/spreadsheets/d/1BaNzUmYlQQ56a9a7txzUSEZhK_B5LRCAvkFlHnZ8L6Q/edit?usp=sharing). The first tab shows all parts currently used in the printer and possible new parts. The second tab shows the lay-out of the GPIO pins that have been used, how the encoders and the relais should be connected. The third tab shows the three ports of the relais.

## Motivation
The earlier printer had as main problem that it printed too slow. We tried to fix this with two modifications:
* Increase the flow by changing the hose
* Substituting the stepper motors by DC-motors with encoders
Since the first isn't that technical, we will now go into detail on how we did the latter.
