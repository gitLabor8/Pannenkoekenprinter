###
# A thread controlling one of the motors
###

from threading import Thread, Event
import queue
from drivers.dc_motor_adafruit_wrapper import MotorWrapper

class MotorThread(Thread):
    # motor: the motor it controls
    # speedQue: an input queue with the requested travelling speed
    def __init__(self, motor: MotorWrapper, speedQ: queue.LifoQueue):
        super(MotorThread, self).__init__()
        self.motor = motor
        self.speedQ = speedQ
        self.stopRequest = Event()

    def run(self):
        while not self.stopRequest.isSet():
            try:
                # Block the call at this point for at most 0.05 seconds
                speed = self.speedQ.get(block=True, timeout=0.05)
                x = self.motor.speedUp(speed)

            except queue.Empty:
                pass

    # What to do when we are stopped
    def join(self, timeout=None):
        self.stopRequest.set()
        super(MotorThread, self).join(timeout)
