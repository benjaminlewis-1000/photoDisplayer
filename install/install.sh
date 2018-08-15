#! /bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

read -p "Would you like to set the Lewis-family only DDNS server? " 
if [[ $REPLY =~ ^[Yy]$ ]]; then
	INSTALL_DDNS=1
else
	INSTALL_DDNS=0
fi

# Default apt-get mirrors aren't working for this version of raspbian; so I wrote a script to update that.
sudo bash $THIS_DIR/subscripts/mirrorSetup.sh

sudo dpkg-reconfigure tzdata

sudo bash $THIS_DIR/subscripts/keyboard.sh

sudo bash $THIS_DIR/subscripts/mountHardDrive.sh

# Apt-get install all the package manager programs I can use. 
sudo bash $THIS_DIR/subscripts/aptGetInstall.sh

#Enable ssh
sudo bash $THIS_DIR/subscripts/sshEnable.sh

# Give permissions to create files from the web interface - used to create database files. 
sudo bash $THIS_DIR/subscripts/chmodChange.sh

# Set the keyboard
sudo setxkbmap -rules xorg -layout us -model pc105

# Install feh and assorted tools
sudo bash $THIS_DIR/subscripts/fehInstall.sh

# Disable screen blanking
sudo sed -i 's/#xserver-command=X/xserver-command=X -s -1 -dpms/' /etc/lightdm/lightdm.conf

sudo bash $THIS_DIR/subscripts/serverInstall.sh

sudo bash $THIS_DIR/subscripts/pyInstall.sh

sudo bash $THIS_DIR/subscripts/cronInstall.sh

sudo bash $THIS_DIR/subscripts/autostart_install.sh

sudo bash $THIS_DIR/subscripts/sambaSetup.sh

sudo bash $THIS_DIR/subscripts/populateDB.sh

if [[ $INSTALL_DDNS ]]; then
    sudo bash $THIS_DIR/optional/ddclientInstall.sh
fi

sudo bash $THIS_DIR/subscripts/chown_files.sh

sudo reboot
#! /bin/bash

