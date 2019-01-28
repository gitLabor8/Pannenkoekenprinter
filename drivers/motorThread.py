
from threading import Thread, Event
import queue
from drivers.dc_motor_adafruit_wrapper import MotorWrapper
import time

class MotorThread(Thread):
    # motor: the motor it controls
    # speedQue: an input queue with the requested speed
    # need to travel
    def __init__(self, motor: MotorWrapper, speedQ: queue.LifoQueue):
        super(MotorThread, self).__init__()
        self.motor = motor
        self.speedQ = speedQ
        self.stopRequest = Event()

    def run(self):
        # print("Started running " + self.name)
        while not self.stopRequest.isSet():
            try:
                # Block the call at this point for at most 0.0005 seconds
                speed = self.speedQ.get(block=True, timeout=0.05)
                # startTime = time.time()
                # print("Thread speed " + str(self.name) + " to " + str(speed))
                x = self.motor.speedUp(speed)
                # print("Thread actual" + str(self.name) + " to " + str(x))
                # endTime = time.time()
                # print(self.name + " - Time: " + str(endTime - startTime))

            except queue.Empty:
                pass

    # What to do when we are stopped
    def join(self, timeout=None):
        self.stopRequest.set()
        super(MotorThread, self).join(timeout)
