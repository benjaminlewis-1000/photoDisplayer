#! /bin/bash


THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"

PHOTO_STR='15 23 * * * /usr/bin/python $PROJECT_ROOT_DIR/pyInit/addPics.py'

CL_STR="15 1 * * * /bin/bash $PROJECT_ROOT_DIR/clTag.sh"
GOOG_STR="15 4 * * * /bin/bash $PROJECT_ROOT_DIR/googTag.sh"

GIT_PULL_STR="* * * * * su -s /bin/sh nobody -c 'cd $PROJECT_ROOT_DIR && /usr/bin/git pull origin master"

#crontab -l ; echo "$CL_STR"    | crontab -
#crontab -l ; echo "$GOOG_STR"  | crontab - 
#crontab -l ; echo "$PHOTO_STR" | crontab -

# Get the current crontab
crontab -l > $THIS_DIR/ccc.cron

# echo "$CL_STR" >> $THIS_DIR/ccc.cron
# echo "$GOOG_STR" >> $THIS_DIR/ccc.cron
echo "$PHOTO_STR" >> $THIS_DIR/ccc.cron
echo "$GIT_PULL_STR" >> $THIS_DIR/ccc.cron

crontab $THIS_DIR/ccc.cron
# rm ccc.cron
