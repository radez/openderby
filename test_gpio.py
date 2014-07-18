#!/usr/bin/python
# Adapted from script by Alex Eames http://RasPi.tv  
# http://RasPi.tv/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3  
import sys
import os
from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO 
GPIO.setmode(GPIO.BCM)

LANE_GPIO_PORTS = [18,17,27,22,23,24]


START_TIME = 0
LANE_TIMES = {}
SHOWN_TIMES = []

# GPIO 23 & 17 set up as inputs, pulled up to avoid false detection.
# Both ports are wired to connect to GND on button press.
# So we'll be setting up falling edge detection for both
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# GPIO 24 set up as an input, pulled down, connected to 3V3 on button press  
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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


#def start_callback(channel):
    
def lane1_callback(channel):
    finish(1)

def lane2_callback(channel):
    finish(2)

def lane3_callback(channel):
    finish(3)

def lane4_callback(channel):
    finish(4)

def lane5_callback(channel):
    finish(5)

def lane6_callback(channel):
    finish(6)

def finish(lane):
    if START_TIME and lane not in LANE_TIMES:
        LANE_TIMES[lane] = datetime.now()
        

## when a rising edge is detected on a lane port the starter callback will be run
#GPIO.add_event_detect(25, GPIO.RISING, callback=start_callback, bouncetime=300)
# when a falling edge is detected on a lane port the finish callback will be run
GPIO.add_event_detect(18, GPIO.FALLING, callback=lane1_callback, bouncetime=300)
GPIO.add_event_detect(17, GPIO.FALLING, callback=lane2_callback, bouncetime=300)
GPIO.add_event_detect(27, GPIO.FALLING, callback=lane3_callback, bouncetime=300)
GPIO.add_event_detect(22, GPIO.FALLING, callback=lane4_callback, bouncetime=300)
GPIO.add_event_detect(23, GPIO.FALLING, callback=lane5_callback, bouncetime=300)
GPIO.add_event_detect(24, GPIO.FALLING, callback=lane6_callback, bouncetime=300)

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
            GPIO.wait_for_edge(25, GPIO.RISING)
            if not START_TIME:
                START_TIME = datetime.now()
                print "Go!"
        for lane in LANE_TIMES:
            if lane not in SHOWN_TIMES: 
                d = LANE_TIMES[lane] - START_TIME
                print "\rlane %i finished in %i.%i seconds" % (lane, d.seconds, d.microseconds)
                SHOWN_TIMES.append(lane)
        sleep(1)
   
    
    except KeyboardInterrupt:
        break

print "Cleaning up GPIO"
GPIO.cleanup()           # clean up GPIO on normal exit
