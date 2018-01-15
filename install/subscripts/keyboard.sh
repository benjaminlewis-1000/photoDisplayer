#! /bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

sudo cp $THIS_DIR/keyboard_conf /etc/default/keyboard
sudo service keyboard-setup restart
sudo udevadm trigger --subsystem-match=input --action=change
