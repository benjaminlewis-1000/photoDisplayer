#! /bin/bash

sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

sudo perl -0777 -p -i -e 's|[# ]+?PermitRootLogin.*|PermitRootLogin yes|g' /etc/ssh/sshd_config

sudo service ssh restart

# Put service ssh start before the exit 0 in rc.local
sudo perl -p -i -e 's|^exit 0|service ssh start\n\nexit 0|g' /etc/rc.local

