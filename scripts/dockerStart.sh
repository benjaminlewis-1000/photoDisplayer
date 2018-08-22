#! /bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

sudo rsyslogd
sudo cron -L15
sudo service apache2 start

python $PROJECT_ROOT_DIR/display/displayServer.py > /dev/null &

# python /app/pyInit/addPics.py --addRootParams --noPhotoAdd
python $PROJECT_ROOT_DIR/display/screenPowerServer.py > /dev/null &
