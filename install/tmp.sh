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


sudo bash $THIS_DIR/subscripts/cronInstall.sh

sudo bash $THIS_DIR/subscripts/autostart_install.sh

sudo bash $THIS_DIR/subscripts/sambaSetup.sh

sudo bash $THIS_DIR/subscripts/populateDB.sh

if [[ $INSTALL_DDNS ]]; then
    sudo bash $THIS_DIR/optional/ddclientInstall.sh
fi

sudo reboot
#! /bin/bash

