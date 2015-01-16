# openderby
OpenSource RPi based Pinewood Derby Timing System

WARNING: This is in its infancy. The code will clean up and evolve often.<br>
WARNING: This hasn't been used to race with yet. If you use it please pass on feed back!


There are three components to the system.
- web service: includes registration, pit view, results view and a current heat status handler
- heat generation script: takes registrations and generates heats
- race controller: cli that interacts with the RPi to run the race

The system is designed around 4 "clients" The expectation is that you would have 1 or more computers at each of
stations except the timer.
- registration<br>
Categories and Car entries are managed here. More computers means faster registration.
- pit<br>
A Web page that auto refreshes displays heat lineups for the pit to stage cars for the race.
Intent is for this page to be displayed and auto refresh itself so that the pit crew doesn't
have to interact with it at all during the race.
- timer<br>
Connected directly to the RPi (montior & keyboard or via ssh) and runs the race controller.
- results<br>
displays results, cached with intent for anyone with an internet connected device to view.

<h3>To get started / registration:</h3>
- python db_reset.py
- python db_seed_test_data.py
- python run_server.py

These steps will setup the database and get the web server running. Categories are created
and Car Registrations can be taken though http://rpi.ip.addpress:8888. The port can be changed in runserver.py

db_seed_test_data is optional. It will give you data to work with. To run your own race reset the database again and
don't seed it with the test data.

<h3>Generating heats:</h3>
- python heat_gen_random.py

This will generate heats from the registrations that have been entered into the system and make sure that
each car will race once on each lane of the track.

<h3>Running the race</h3>
- python race_controller.py [test]

This script will interact with the RPi to collect the race data and write it to the database. It will also send
the current category and heat back to the webserver for the pit page.

The test option will load the mock_GPIO module and will simulate the start gate and finish line based on randomly
generated times for the start gate and lanes on the finish line.
At "Waiting for Start" test mode will wait 1-5 seconds and trigger start.
When a heat is running each lane will wait between 10 and 20 seconds to trigger finishing for each lane.

<h3>Web Server URLs</h3>
- Results (5 sec cache): /
- Registration: /registration
- Pit (5 sec cache): /pit
- Status (json output): /status
- Update Status (json output): /status/&lt;category_id&gt;/&lt;heat_id&gt;

