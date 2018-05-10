#!/usr/bin/python
# Adapted from script by Alex Eames http://RasPi.tv  
# http://RasPi.tv/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3  
# Captured key press events with
# http://stackoverflow.com/questions/13207678/whats-the-simplest-way-of-detecting-keyboard-input-in-python-from-the-terminal
import sys
import os
sys.stdout.write('Importing requests library')
sys.stdout.flush()
import requests
import threading

from openderby.models import app, Category, Car, Heat

http_server = '192.168.0.254'
http_port = '9000'

# for RPI version 1, use "bus = smbus.SMBus(0)"
try:
    import smbus
    bus = smbus.SMBus(1)
except:
    bus = None

# This is the address we setup in the Arduino Program
address = 0x04

class UpdateScoreboard(threading.Thread):
    def run(self):
        r = requests.get('http://%s:%s/scoreboard_update' % (http_server, http_port))
        if r.status_code != 200:
            print "SCOREBOARD UPDATE FAILED %s" % r.text

def pitWrite(value):
    value = list(value)
    value.reverse()
    while len(value):
        x = ord(value.pop())
        try:
            bus.write_byte(address, x)
        except:
            print "Failed to write %s to the pit" % x
    # bus.write_byte_data(address, 0, value)

from time import sleep
from datetime import datetime
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    import race_controller_mock_GPIO as GPIO
    print "\nUsing mock_GPIO module"
    pitWrite = lambda x: True
    print "Overloading pitWrite"
else:
    import RPi.GPIO as GPIO 

GPIO.setmode(GPIO.BCM)

sys.stdout.write('\r                          ')
sys.stdout.write('\rTesting Pit connectivity')
sys.stdout.flush()
pitWrite(' ')
# Import OpenDerby database
sys.stdout.write('\r                          ')
sys.stdout.write('\rConnecting to database')
sys.stdout.flush()

# GPIO port assignments
START = 25
LANE1 = 18
LANE2 = 17
LANE3 = 27
LANE4 = 22
LANE5 = 23
LANE6 = 24
GATE  = 04

LANE_GPIO_PORTS = [LANE1,LANE2,LANE3,LANE4,LANE5,LANE6]
LANES = {LANE1: 1, LANE2: 2,
         LANE3: 3, LANE4: 4,
         LANE5: 5, LANE6: 6 }



# GPIO for lanes set up as inputs, pulled down
GPIO.setup(LANE1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LANE2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LANE3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LANE4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LANE5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LANE6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# GPIO 25 set up as an input, pulled down, connected to 3V3 on button press  
GPIO.setup(START, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def ready_or_not(port):
    msg = 'READY'
    if not GPIO.input(port):
        msg = 'NOT ' + msg
    return msg

def sensor_test(w_start = True):
    while 1:
        if w_start:
            ports = LANE_GPIO_PORTS + [START]
        else:
            ports = LANE_GPIO_PORTS
        if reduce(lambda x,y: x and GPIO.input(y), ports):
            break
        os.system('clear')
        if w_start:
            print 'start  :: port %i :: %s' % (START, ready_or_not(START))
        for i in LANE_GPIO_PORTS:
            print 'lane %s :: port %i :: %s' % (LANES[i], i, ready_or_not(i))
        raw_input("Press Enter to continue")

def finishline_callback(port):
    #print port
    if START_TIME and not LANE_TIMES[port]:
        LANE_TIMES[port] = datetime.now()
        

## when a rising edge is detected on a lane port the starter callback will be run
#GPIO.add_event_detect(25, GPIO.RISING, callback=start_callback, bouncetime=300)
# when a falling edge is detected on a lane port the finish callback will be run
GPIO.add_event_detect(LANE1, GPIO.FALLING, callback=finishline_callback)#, bouncetime=300)
GPIO.add_event_detect(LANE2, GPIO.FALLING, callback=finishline_callback)#, bouncetime=300)
GPIO.add_event_detect(LANE3, GPIO.FALLING, callback=finishline_callback)#, bouncetime=300)
GPIO.add_event_detect(LANE4, GPIO.FALLING, callback=finishline_callback)#, bouncetime=300)
GPIO.add_event_detect(LANE5, GPIO.FALLING, callback=finishline_callback)#, bouncetime=300)
GPIO.add_event_detect(LANE6, GPIO.FALLING, callback=finishline_callback)#, bouncetime=300)

START_TIME = 0
LANE_TIMES = dict(zip(LANE_GPIO_PORTS, [0,0,0,0,0,0]))
SHOWN_TIMES = []

CATEGORY = 0
HEAT = 0
HEAT_LANES = 0
HEAT_LANE_PORTS = []
HEAT_CT = 0

def pit_update(category, heat):
    pitWrite(' ')
    lanes = Heat.query.filter_by(id=heat, category_id=category).order_by("lane").all()
    lane_update = 1
    for heat in lanes:
        while lane_update != heat.lane:
            pitWrite(':::')
            lane_update+=1
        pitWrite('{::>3}'.format(heat.car.id))
        lane_update+=1

def status_update(category, heat):
    if category:
        category = category.id
    r = requests.get('http://%s:%s/status/%s/%s' % (http_server, http_port, category, heat))
    if r.status_code != 200:
        print "STATUS UPDATE FAILED %s" % r.text

def finish_update(lane, time):
    try:
        r = requests.get('http://%s:%s/finish/%s/%s/' % (http_server, http_port, lane, time))
        if r.status_code != 200:
            print "FINISH UPDATE FAILED %s" % r.text
    except:
        pass
pitWrite
sys.stdout.write('\r                          ')
sys.stdout.write('\rSensor Test\n')
sensor_test()
sys.stdout.write('\r                          \r')

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
                        app.db.session.add(heat)
                        app.db.session.commit()
                        # heat.time rounds ten-hundred-thousands
                        print "\rLane %i: %f" % (LANES[port], heat.time)
                        # Highest accuracy treat seconds and microseconds separatly
                        #print "\rLane %i: %i.%i" % (LANES[port], d.seconds, d.microseconds)
                        SHOWN_TIMES.append(port)
                        finish_update(LANES[port], heat.time)

        elif not CATEGORY:
            while CATEGORY == 0:
                #os.system('clear')
                print "Getting category list"
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
                status_update(CATEGORY, HEAT)
                pit_update(CATEGORY.id, HEAT)
                UpdateScoreboard().start()
        else:
            # update the status thread
            #os.system('clear')
            status_update(CATEGORY, HEAT)
            # check that we can still see all the sensors
            # ignore start gate, that will be checked separate here
            sensor_test(False)
            # print the category and heat
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
            go = 0
            while go < 3:
                #GPIO.wait_for_edge(START, GPIO.FALLING)
                # software debounce
                go = 0
                for i in [1,2,3]:
                    sleep(.01)
                    go += int(not GPIO.input(START))
            if not START_TIME:
                START_TIME = datetime.now()
                # need the spaces to overwrite
                # waiting for start
                print "\rGo!              "
                pit_update(CATEGORY.id, HEAT+1)
                UpdateScoreboard().start()
        sleep(.5)
  
    
    except KeyboardInterrupt:
        break

#print "Cleaning up GPIO"
GPIO.cleanup()           # clean up GPIO on normal exit
