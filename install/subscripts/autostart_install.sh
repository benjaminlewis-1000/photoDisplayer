#! /bin/bash

mkdir -p ~/.config/autostart

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"
echo $PROJECT_ROOT_DIR

echo "[Desktop Entry]" > $PROJECT_ROOT_DIR/scripts/display.desktop
echo "Name=Pi_Photo" >>  $PROJECT_ROOT_DIR/scripts/display.desktop
echo "Exec=$PROJECT_ROOT_DIR/display/displayServer.py" >>  $PROJECT_ROOT_DIR/scripts/display.desktop
echo "Type=application" >> $PROJECT_ROOT_DIR/scripts/display.desktop

cp $PROJECT_ROOT_DIR/scripts/display.desktop ~/.config/autostart
cp $PROJECT_ROOT_DIR/scripts/remote.desktop ~/.config/autostart
