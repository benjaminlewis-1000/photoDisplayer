#! /bin/bash

PHOTO_STR='15 23 * * * /usr/bin/python/home/pi/photoDisplayer/pyInit/addPics.py'

CL_STR='15 1 * * * /bin/bash /home/pi/photoDisplayer/clTag.sh'
GOOG_STR='15 4 * * * /bin/bash /home/pi/photoDisplayer/googTag.sh'

#crontab -l ; echo "$CL_STR"    | crontab -
#crontab -l ; echo "$GOOG_STR"  | crontab - 
#crontab -l ; echo "$PHOTO_STR" | crontab -

echo "$CL_STR" >> ccc.cron
echo "$GOOG_STR" >> ccc.cron
echo "$PHOTO_STR" >> ccc.cron

crontab ccc.cron
rm ccc.cron
