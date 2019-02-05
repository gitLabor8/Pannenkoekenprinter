# NDL Pannenkoekenprinter report
Frank Gerlings, s4384873 - Januari 2019

This readme explains the structure of the code and the design decisions. For a list
 of all the necessary equipment and a user guide, see ``documentation > 
 Gebruikshandleiding.md``. These are separated for the convenience of the people 
that use the project for demonstrations.

## Motivation
The earlier printer had as main problem that the stepper motors vibrated too much 
and that it printed too slow. We tried to fix this with two modifications:
* Substituting the stepper motors by DC-motors with encoders
* Increase the flow by changing the hose
In this README we will mainly focus on the fist one, since it is the most code 
related.

## Code structure
* ``./runme.py``: operates as TUI, is the main file of the project.
* ``./fileReader.py``: parses an opened file and transformes the file input into a
 printable array of vectors.
* ``./drivers/``: ``dc_motor.py`` prints vectors. The rest of the folder is filled with 
files containing auxiliary classes. This is the main logic of the project. We will
 elaborate on it later in this README.
* ``./test_drivers.py``: contains multiple tests that test several mathematical 
functions
* ``./documentation/``: contains more background information on this project, in 
particular ``Pannenkoekenprinter Gebruikshandleiding.pdf``.
* ``./examples/``: contains all example files that the printer currently can print. 
More can be added, should the user feel the need to.

## Physical components
An overview can be found in 
[this spreadsheet](https://docs.google
.com/spreadsheets/d/1BaNzUmYlQQ56a9a7txzUSEZhK_B5LRCAvkFlHnZ8L6Q/edit?usp=sharing)
, but is also given in ``./documentation/Spreadsheets.pdf``. 
The first tab shows all parts currently used in the printer and possible new 
parts. The second tab shows the lay-out of the GPIO pins that have been used, how 
the encoders and the relais should be connected. The third tab shows the three ports of the relais.
The last tab compares the x- and y-motor with each other in terms of measuring 
points and speed.

## Notable libraries
- adafruit-circuitpython-motorkit: Used to control the speed of the motors through the pi motor HAT
- RPi.GPIO: Used to read the measurements of the encoders and used to toggle the relais of the pump

## Early approach
In my first approach we calculated the relative speeds of the motors and just 
revved up the motors to these speeds. To determine if we should stop we would 
check if we would get any closer. If so, we would continue. If not, we would stop.
The downside of this approach is that we cannot change our course during the ride.
So should one motor happen to be slower than planned, he cannot compensate. We 
therefore went for another approach. We kept the mechanism that aborts once we do 
not get closer anymore as a fail safe in the final design.

## Final approach
General idea:
 - Coordinate systems: The encoders give us about 1800 measuring points in both directions. However, the pan is not that large, so we set our actual drawing frame smaller
 - Reset posistion: To reset the position of the printerhead, we simply move backwards untill we don't get any new measuring points. Since that means that we are not moving any further, we've apparently reached the bottom left corner of the printer. As mentioned before, our drawing frame is smaller, so we take a small offset upwards and to the right to reach the zero point of the drawing frame.
 - Move to a specific coordinate: we will elaborate on this in the following points where we encounter a problem and then solve it.

### Diagonal lines
The first thing we do when we want to print a line is compute the base speeds. For example, if we need to go from (0, 0) to (100, 200) then we will give the y-motor run the maximum as base speed and we scale x down to only the half of the maximum.

### Accidentally getting of track
For all kinds of magical reasons, we could get off track. This is why we let both 
motors run on 90% of their normal speed. Should one get behind, we can speed it up
to 100% of the speed. Should a motor get ahead of its position, we can slow it 
down to 80% of it's normal speed.

### Where do we need to be?
To find out where we wanted to keep track of our expected path. To do this, we tried to use the Python Geometry library. However, it seemed to be way to slow in computing, since it wanted keep exact track of our position, rather than focussing on execution speed. Similarly we tried to use Shapely, which is a wrapper of the C++ codebase GEOS. Since it is in C++, we expected it to be faster, but to avail. Finally we went for a selfmade class, named ``./drivers/path.py``. We would initialise it with our starting and ending positions and upon giving it our current distance of the target it would simply return the it's expected position.

### Ramping
The motors cannot be set to a high speed and be expected to immediately run at 
said speed, they need to ramp up to that speed in order to work. Doing this 
naively gave us two problems:
- when a motor sped up, it would not stop speeding up until it reached that speed,
 even when it would already have surpassed the point that it had to reach
- when one motor sped up, the other slowed down
The first problem can be solved by incrementing the motors with a maximum amount 
and then check again for a new speed. We choose this maximum amount to be 5% of 
the full speed. Code for this can be found in ``dc_motor_adafruit_wrapper.py``.
We solved the second problem by creating one extra thread per motor, see 
``motorThread.py``. ``dc_motor.py`` would keep on measuring and sending freshly 
calculated speeds to the motor threads.

### Overshoot the destination
A similar process as ramping happens when decreasing speed. In early development 
we tended to overshoot our destination because of this. Therefore we implemented a
function that gradually slows down the base speed when nearing the destination. 
This has the caveat that lines get thicker at the end. To accommodate for this we 
disable the pump at a certain fixed distance from the end.

### Minimal speed
The motors have a base amount of resistance they encounter, namely the weight they need to move. Therefore they need a certain base speed to actually move. When we combine this with earlier mentioned solutions, we can see that the motor sometimes might fall still too early, should we naively scale the motor down to a speed of zero. Instead we introduced a minimal speed at which a motor should operate and once we are close enough to the target we completely shut down the motor.

### Default measuring deviation
As shown in tab 4 of the spreadsheets, the x-measuring values have about 
0,7% deviation and the y-measuring values have an even higher deviation, of about 2%.
This means that even when our program thinks he is at the perfect position, he 
might still be off quite a bit. This is why after printing a vector we check if 
we've already moved a lot. If so, we reset the position of the motor, effectively 
recalibrating the motors.

## Hose change
The hose was changed for one with a bigger throughput. This worked in the sense 
that the throughput got significantly bigger. However, this caused the drawn lines 
to be very broad. We used a clip to decrease the throughput. This worked upon 
till a certain point where the flow starting to drip, rather than be continuous.
We leave it up to the user if he prefers drawing speed or detailed pictures.

## Future work
Possible improvements can be made in the following area's:
- Input through:
    + upgrading the TUI to function via a Telegram bot
    + a webpage that can be visited by connecting to a wifi network run on the pi
    + a drawing app, users can print self drawn pancakes
    + pictures. The old forked code can probably still be used
- Setting up a hotspot with a WiPi, so a laptop or other input device can connect 
without the use of the router and its accompanying cable works.
 
