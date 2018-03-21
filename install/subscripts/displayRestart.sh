#! /bin/bash

# A script to be run once a day that will restart the display server without restarting the raspberry pi; allows for updates to the server.

export DISPLAY=:0

DISPLAY_SERVER_PID=$(ps aux | grep displayServer.py | grep -v grep | grep python | awk '{print $2}') 

echo $DISPLAY_SERVER_PID

kill -9 $DISPLAY_SERVER_PID

FEH_PID=$(ps aux | grep feh | grep -v grep | grep -v defunct | awk '{print $2}')

kill -9 $FEH_PID

# nohup bash -c "(<ROOTDIR>/display/displayServer.py)" &
python (<ROOTDIR>/display/displayServer.py) &
