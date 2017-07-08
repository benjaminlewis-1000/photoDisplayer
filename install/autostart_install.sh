#! /bin/bash

mkdir -p ~/.config/autostart

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cp $THIS_DIR/display.desktop ~/.config/autostart
cp $THIS_DIR/remote.desktop ~/.config/autostart
