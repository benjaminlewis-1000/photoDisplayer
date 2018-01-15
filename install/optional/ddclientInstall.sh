#! /bin/bash

sudo apt-get install ddclient -y

USERNAME=benjaminlewis
PASSWORD=throwawaydns

read -r -d '' DD_CONFIG << EOM
# ddclient configuration for Dynu \n
# \n
# Configuration file from http://www.dynu.com/DynamicDNS/IPUpdateClient/DDClient \n
#  \n
# /etc/ddclient.conf \n
daemon=60   #  Check every 60 seconds \n
syslog=yes \n
mail=root \n
mail-failure=root\n
pid=/var/run/ddclient.pid\n\
\n
use=web, web=checkip.dynu.com/, web-skip='IP Address'\n
server=api.dynu.com\n
protocol=dyndns2\n
login=$USERNAME\n
password=$PASSWORD\n
lewisfamily.ddnsfree.com\n
EOM

rm ddclient.conf
echo -e $DD_CONFIG > ddclient.conf

sudo cp ddclient.conf /etc/ddclient.conf 

sudo chown $USER /etc/ddclient.conf

rm ddclient.conf

sudo /usr/sbin/ddclient -daemon 300 -syslog
