#! /bin/bash

# Get the current working directory as well as the one two up (assume that the file heiarchy is still in place)
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"

PHOTO_STR="15 23 * * * /usr/bin/python $PROJECT_ROOT_DIR/pyInit/addPics.py"

CL_STR="15 1 * * * /bin/bash $PROJECT_ROOT_DIR/scripts/clTag.sh"
GOOG_STR="15 4 * * * /bin/bash $PROJECT_ROOT_DIR/scripts/googTag.sh"

GIT_PULL_STR="0 1 * * * $PROJECT_ROOT_DIR/scripts/gitpull.sh"
RESTART_DISPLAY_STR="0 1 * * * $PROJECT_ROOT_DIR/scripts/displayRestart.sh"

SCREEN_SERVER_STR="@reboot python $PROJECT_ROOT_DIR/display/screenPowerServer.py &"

sudo chown $USER $PROJECT_ROOT_DIR/scripts/gitpull.sh

echo "#! /bin/bash" > $PROJECT_ROOT_DIR/scripts/gitpull.sh
echo "cd $PROJECT_ROOT_DIR" >> $PROJECT_ROOT_DIR/scripts/gitpull.sh
echo "git pull" >> $PROJECT_ROOT_DIR/scripts/gitpull.sh
chmod +x $PROJECT_ROOT_DIR/scripts/gitpull.sh

# echo "gitpull.sh" >> $PROJECT_ROOT_DIR/.gitignore

#crontab -l ; echo "$CL_STR"    | crontab -
#crontab -l ; echo "$GOOG_STR"  | crontab - 
#crontab -l ; echo "$PHOTO_STR" | crontab -

# Get the current crontab
crontab -l > $THIS_DIR/ccc.cron

# echo "$CL_STR" >> $THIS_DIR/ccc.cron
# echo "$GOOG_STR" >> $THIS_DIR/ccc.cron
echo "$PHOTO_STR" >> $THIS_DIR/ccc.cron
echo "$GIT_PULL_STR" >> $THIS_DIR/ccc.cron
echo "$RESTART_DISPLAY_STR" >> $THIS_DIR/ccc.cron
echo "$SCREEN_SERVER_STR" >> $THIS_DIR/ccc.cron


cp $THIS_DIR/displayRestart.sh $PROJECT_ROOT_DIR/scripts/displayRestart.sh
# use commas because we don't want to cue on slashes
sed -i  "s,<ROOTDIR>,$PROJECT_ROOT_DIR," $PROJECT_ROOT_DIR/scripts/displayRestart.sh


crontab $THIS_DIR/ccc.cron
