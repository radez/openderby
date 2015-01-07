
LANE1 = 18
LANE2 = 17
LANE3 = 27
LANE4 = 22
LANE5 = 23
LANE6 = 24
LANE_GPIO_PORTS = [LANE1,LANE2,LANE3,LANE4,LANE5,LANE6]

BCM = None
IN = None
PUD_DOWN = None
RISING = None
FALLING = None

# interupt like behaviour mocked from
# http://code.activestate.com/recipes/203830-checking-for-a-keypress-without-stop-the-execution/

import threading
import time 
from random import randint

class Monitor(threading.Thread):
    def __init__(self, lane, callback):
        threading.Thread.__init__(self)
        self.lane = lane
        self.callback = callback

    def run(self):
        while 1:
            time.sleep(randint(10,20))
            self.callback(self.lane)
        

key_thread = None

def setmode(x):
    pass

def setup(*args, **kwargs):
    pass

def input(*args, **kwargs):
    return True

def add_event_detect(*args, **kwargs):
    x = Monitor(args[0], kwargs['callback'])
    # dies when parent dies
    x.daemon = True
    x.start()

def wait_for_edge(*args, **kwargs):
    time.sleep(randint(1,5))

def cleanup():
    pass
