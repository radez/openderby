#!/usr/bin/python
# Adapted from script by Alex Eames http://RasPi.tv  
# http://RasPi.tv/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3  
import sys
import os
from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO 
GPIO.setmode(GPIO.BCM)

# GPIO port assignments
START = 25
LANE1 = 18
LANE2 = 17
LANE3 = 27
LANE4 = 22
LANE5 = 23
LANE6 = 24

LANE_GPIO_PORTS = [LANE1,LANE2,LANE3,LANE4,LANE5,LANE6]
LANES = {LANE1: 1, LANE2: 2,
         LANE3: 3, LANE4: 4,
         LANE5: 5, LANE6: 6 }


START_TIME = 0
LANE_TIMES = {}
SHOWN_TIMES = []

# GPIO 23 & 17 set up as inputs, pulled up to avoid false detection.
# Both ports are wired to connect to GND on button press.
# So we'll be setting up falling edge detection for both
GPIO.setup(LANE1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LANE2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LANE3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LANE4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LANE5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LANE6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# GPIO 24 set up as an input, pulled down, connected to 3V3 on button press  
GPIO.setup(START, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def ready_or_not(port):
    msg = 'READY'
    if not GPIO.input(i):
        msg = 'NOT ' + msg
    return msg

# verify setup
while 1:
    for i in LANE_GPIO_PORTS:
        print 'port %i %s' % (i, ready_or_not(i))
    raw_input("Press Enter to continue")
    os.system('clear')
    if reduce(lambda x,y: x and GPIO.input(y), LANE_GPIO_PORTS):
        break 

def finishline_callback(port):
    if START_TIME and port not in LANE_TIMES:
        LANE_TIMES[port] = datetime.now()
        

## when a rising edge is detected on a lane port the starter callback will be run
#GPIO.add_event_detect(25, GPIO.RISING, callback=start_callback, bouncetime=300)
# when a falling edge is detected on a lane port the finish callback will be run
GPIO.add_event_detect(LANE1, GPIO.FALLING, callback=finishline_callback, bouncetime=300)
GPIO.add_event_detect(LANE2, GPIO.FALLING, callback=finishline_callback, bouncetime=300)
GPIO.add_event_detect(LANE3, GPIO.FALLING, callback=finishline_callback, bouncetime=300)
GPIO.add_event_detect(LANE4, GPIO.FALLING, callback=finishline_callback, bouncetime=300)
GPIO.add_event_detect(LANE5, GPIO.FALLING, callback=finishline_callback, bouncetime=300)
GPIO.add_event_detect(LANE6, GPIO.FALLING, callback=finishline_callback, bouncetime=300)

while 1:

    try:
        if len(SHOWN_TIMES) >= 6:
            break
        if START_TIME:
            d = datetime.now() - START_TIME
            sys.stdout.write('\r%i.%i' % (d.seconds, d.microseconds))
            sys.stdout.flush()
        else:
            print "Waiting for start"
            GPIO.wait_for_edge(START, GPIO.RISING)
            if not START_TIME:
                START_TIME = datetime.now()
                print "Go!"
        for port in LANE_TIMES:
            if port not in SHOWN_TIMES: 
                d = LANE_TIMES[port] - START_TIME
                print "\rlane %i finished in %i.%i seconds" % (LANES[port], d.seconds, d.microseconds)
                SHOWN_TIMES.append(port)
        sleep(1)
   
    
    except KeyboardInterrupt:
        break

print "Cleaning up GPIO"
GPIO.cleanup()           # clean up GPIO on normal exit
