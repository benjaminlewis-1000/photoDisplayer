#! /bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

# Apt-get install all the package manager programs I can use. 
sudo bash $THIS_DIR/subscripts/aptGetInstall.sh

# Give permissions to create files from the web interface - used to create database files. 
sudo bash $THIS_DIR/subscripts/chmodChange.sh

sudo cp $THIS_DIR/keyboard /etc/default/keyboard

# Install feh and assorted tools
sudo bash $THIS_DIR/subscripts/fehInstall.sh

# Disable screen blanking
sudo sed -i 's/#xserver-command=X/xserver-command=X -s 0 -dpms/' /etc/lightdm/lightdm.conf

sudo bash $THIS_DIR/serverInstall.sh

sudo bash $THIS_DIR/pyInstall.sh

sudo bash $THIS_DIR/populateDB.sh

sudo bash $THIS_DIR/cronInstall.sh

sudo bash $THIS_DIR/subscripts/mountHardDrive.sh




