#! /bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

sudo perl -0777 -p -i -e 's|[# ]+?PermitRootLogin.*|PermitRootLogin no|g' /etc/ssh/sshd_config
sudo perl -0777 -p -i -e 's|[# ]+?UsePAM.*|UsePAM no|g' /etc/ssh/sshd_config
sudo perl -0777 -p -i -e 's|[# ]+?PasswordAuthentication.*|PasswordAuthentication no|g' /etc/ssh/sshd_config

sudo service ssh restart

# Put service ssh start before the exit 0 in rc.local
sudo perl -p -i -e 's|^exit 0|service ssh start\n\nexit 0|g' /etc/rc.local

mkdir ~/.ssh
sudo chown $USER ~/.ssh
sudo chmod 700 ~/.ssh
sudo cp $THIS_DIR/lewis_family_id_rsa.pub ~/.ssh

cat ~/.ssh/lewis_family_id_rsa.pub >> ~/.ssh/authorized_keys
sudo chmod 644 ~/.ssh/authorized_keys
