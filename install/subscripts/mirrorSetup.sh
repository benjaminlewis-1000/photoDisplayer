#! /bin/bash

OS_VERSION=`cat /etc/os-release | grep VERSION= | awk -F"[()]" '{print $2}'`

read -r -d '' SOURCES_LIST << EOM
deb http://mirror.ox.ac.uk/sites/archive.raspbian.org/archive/raspbian $OS_VERSION main contrib non-free rpi
EOM

echo $SOURCES_LIST

sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak

sudo echo -e $SOURCES_LIST > /etc/apt/sources.list
