#! /bin/bash

# A script to be run once a day that will restart the display server without restarting the raspberry pi; allows for updates to the server.

DISPLAY_SERVER_PID=$(ps aux | grep displayServer.py | head -1 | awk '{print $2}') 

echo $DISPLAY_SERVER_PID

kill -9 $DISPLAY_SERVER_PID

(<ROOTDIR>/display/displayServer.py &)
