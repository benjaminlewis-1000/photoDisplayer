#! /bin/bash

# sudo apt-get update -y
# sudo apt-get upgrade -y 
# sudo apt-get install samba samba-common-bin -y

SAMBA_SHARE="
[share]
Comment = Pi shared folder
Path = /mnt/photo_drive
Browseable = yes
Writeable = yes
only guest = no
create mask = 0777
directory mask = 0777
Public = yes
Guest ok = yes"

sudo chown $USER /etc/samba/smb.conf
sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak

echo -e "$SAMBA_SHARE" | tee -a /etc/samba/smb.conf

sudo /etc/init.d/samba restart
