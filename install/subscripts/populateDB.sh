#! /bin/bash

PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"

# Kill any process running python geoServer.py (not necessary on install, but nevertheless kills it off nicely and this is a nice line to have around.
GEOSERVER_PID=$(ps aux | grep geoServer.py | head -1 | awk '{print $2}')
kill -9 $GEOSERVER_PID

# Create the photo database
perl $PROJECT_ROOT_DIR/pyInit/database_create.pl

# Add pictures in the mount drive location (default). While the photo database software is capable of more than one root directory, this is the most simple root directory and we, in the end, want the pictures on that drive. 
python $PROJECT_ROOT_DIR/pyInit/addPics.py --addRoot /mnt/photo_drive

perl $PROJECT_ROOT_DIR/visionTagging/visDatabaseCreate.pl
