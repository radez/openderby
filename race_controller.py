#!/usr/bin/python
# Adapted from script by Alex Eames http://RasPi.tv  
# http://RasPi.tv/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3  
import sys
import os
import requests

from time import sleep
from datetime import datetime
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    import mock_GPIO as GPIO
    print "Using mock_GPIO module"
else:
    import RPi.GPIO as GPIO 

GPIO.setmode(GPIO.BCM)

# Import OpenDerby database
from openderby import db
from registration import Category, Car, Heat

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
    if not GPIO.input(port):
        msg = 'NOT ' + msg
    return msg

# verify setup
print "Sensor Test"

while 1:
    os.system('clear')
    print 'start  :: port %i :: %s' % (START, ready_or_not(START))
    for i in LANE_GPIO_PORTS:
        print 'lane %s :: port %i :: %s' % (LANES[i], i, ready_or_not(i))
    raw_input("Press Enter to continue")
    #os.system('clear')
    if reduce(lambda x,y: x and GPIO.input(y), LANE_GPIO_PORTS):
        break 

def finishline_callback(port):
    #print port
    if START_TIME and not LANE_TIMES[port]:
        LANE_TIMES[port] = datetime.now()
        

## when a rising edge is detected on a lane port the starter callback will be run
#GPIO.add_event_detect(25, GPIO.RISING, callback=start_callback, bouncetime=300)
# when a falling edge is detected on a lane port the finish callback will be run
GPIO.add_event_detect(LANE1, GPIO.FALLING, callback=finishline_callback, bouncetime=0)#300)
GPIO.add_event_detect(LANE2, GPIO.FALLING, callback=finishline_callback, bouncetime=0)#300)
GPIO.add_event_detect(LANE3, GPIO.FALLING, callback=finishline_callback, bouncetime=0)#300)
GPIO.add_event_detect(LANE4, GPIO.FALLING, callback=finishline_callback, bouncetime=0)#300)
GPIO.add_event_detect(LANE5, GPIO.FALLING, callback=finishline_callback, bouncetime=0)#300)
GPIO.add_event_detect(LANE6, GPIO.FALLING, callback=finishline_callback, bouncetime=0)#300)

START_TIME = 0
LANE_TIMES = dict(zip(LANE_GPIO_PORTS, [0,0,0,0,0,0]))
SHOWN_TIMES = []

CATEGORY = 0
HEAT = 0
HEAT_LANES = 0
HEAT_LANE_PORTS = []
HEAT_CT = 0

def status_update(category, heat):
    if category:
         category = category.id
    r = requests.get('http://localhost:8888/status/%s/%s' % (category, heat))
    if r.status_code != 200:
        print "STATUS UPDATE FAILED %s" % r.text


while 1:
    try:
        #if len(SHOWN_TIMES) >= 6:
        #    break
        if START_TIME:
            if len(SHOWN_TIMES) >= len(HEAT_LANES):
                # All lanes have gotten a time
                # Reset for next heat
                START_TIME = 0
                LANE_TIMES = dict(zip(LANE_GPIO_PORTS, [0,0,0,0,0,0]))
                SHOWN_TIMES = []
                HEAT+=1
                if HEAT > HEAT_CT:
                    CATEGORY = 0
                    HEAT = 0
                    status_update(CATEGORY, HEAT)
            else:    
                d = datetime.now() - START_TIME
                sys.stdout.write('\r%i.%i' % (d.seconds, d.microseconds))
                sys.stdout.flush()
                for port in LANE_TIMES:
                    if LANE_TIMES[port] and port in HEAT_LANE_PORTS and port not in SHOWN_TIMES: 
                        d = LANE_TIMES[port] - START_TIME
                        heat = Heat.query.filter_by(id=HEAT, category=CATEGORY, lane=LANES[port]).first()
                        heat.time = float("%s.%s" % (d.seconds, d.microseconds)) 
                        db.session.add(heat)
                        db.session.commit()
                        # heat.time rounds ten-hundred-thousands
                        print "\rLane %i: %f" % (LANES[port], heat.time)
                        # Highest accuracy treat seconds and microseconds separatly
                        #print "\rLane %i: %i.%i" % (LANES[port], d.seconds, d.microseconds)
                        SHOWN_TIMES.append(port)

        elif not CATEGORY:
            while CATEGORY == 0:
                #os.system('clear')
                for cat in Category.query.all():
                    print "%s: %s" % (cat.id, cat.name)
                print "x: Exit"
                print ""
                cat_id = raw_input("Select Category Number: ")
                if cat_id.lower() == "x":
                    exit(0)
                CATEGORY = Category.query.filter_by(id=cat_id).first()
                heat_id = raw_input("Enter a Heat to start with (%s): " % str(HEAT+1))
                if not heat_id:
                    HEAT = HEAT+1
                else:
                    HEAT = int(heat_id) 
        else:
            # update the status thread
            #os.system('clear')
            status_update(CATEGORY, HEAT)
            print "\nCategory: %s" % CATEGORY.name
            HEAT_CT = len(Heat.query.filter_by(category=CATEGORY).group_by('id').all())
            print "Total Heats: %s" % HEAT_CT
            print ""
            HEAT_LANES = Heat.query.filter_by(category=CATEGORY).filter_by(id=HEAT).order_by('lane').all()
            HEAT_LANE_PORTS = map(lambda x: LANE_GPIO_PORTS[x.lane-1], HEAT_LANES)
            print "Heat %s: %s Lanes" % (str(HEAT), str(len(HEAT_LANES)))
            for l in HEAT_LANES:
                print "Lane %s: %s (%s)" % (l.lane, l.car.name, l.car.driver)

            print ""
            gate_settle = 5
            while 1:
                sys.stdout.write("\rWaiting for gate")
                if not gate_settle:
                    break
                elif GPIO.input(START):
                    gate_settle-=1
                    sys.stdout.write(": %s" % str(gate_settle + 1))
                else:
                    if gate_settle != 5:
                         sys.stdout.write("    ")
                    gate_settle = 5
                sys.stdout.flush()
                sleep(1)

            # clear the line first
            sys.stdout.write("\r                   ")
            sys.stdout.write("\rWaiting for start")
            sys.stdout.flush()
            GPIO.wait_for_edge(START, GPIO.FALLING)
            if not START_TIME:
                START_TIME = datetime.now()
                # need the spaces to overwrite
                # waiting for start
                print "\rGo!              "
        sleep(1)
  
    
    except KeyboardInterrupt:
        break

#print "Cleaning up GPIO"
GPIO.cleanup()           # clean up GPIO on normal exit
