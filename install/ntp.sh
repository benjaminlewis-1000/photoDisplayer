#! /bin/bash

sudo apt-get install ntp  -y

sudo dpkg-reconfigure tzdata

sudo cp /etc/ntp.conf /etc/ntp.conf.bak

sudo sed -i 's/restrict /# restrict /g' /etc/ntp.conf

echo "server 0.north-america.pool.ntp.org iburst" | sudo tee -a /etc/ntp.conf
echo "server 1.north-america.pool.ntp.org iburst" | sudo tee -a /etc/ntp.conf
echo "server 2.north-america.pool.ntp.org iburst" | sudo tee -a /etc/ntp.conf
echo "server 3.north-america.pool.ntp.org iburst" | sudo tee -a /etc/ntp.conf

sudo /etc/init.d/ntp restart
