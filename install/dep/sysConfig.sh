#! /bin/bash

# Disable screen blanking. Will need a system restart or a 'sudo service
# lightdm restart' to take effect.
echo "xserver-command=X -s 0 dpms" | sudo tee -a /etc/lightdm/lightdm.conf

sudo perl -0777 -p -i -e 's/XKBLAYOUT=.*/XKBLAYOUT="us"/' /etc/default/keyboard
