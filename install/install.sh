#! /bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

# Give permissions to create files from the web interface - used to create database files. 
chmod 777 $PROJECT_ROOT_DIR/site
chmod 777 $PROJECT_ROOT_DIR/site/scripts_controlpanel

echo $THIS_DIR

sudo cp $THIS_DIR/keyboard /etc/default/keyboard

sudo apt-get update
sudo apt-get install vim -y
sudo apt-get install nautilus -y

# Install CEC packages - these let you, in theory, control the TV from the computer.

sudo apt-get install cec-utils libcec-dev libraspberrypi-dev -y

# Install Expect scripting - allows us to use GUIs automatically 

sudo apt-get install expect -y
sudo apt-get install xinput -y 

sudo expect $THIS_DIR/expect_scripts/ssh.exp
sudo expect $THIS_DIR/expect_scripts/boot.exp
sudo expect $THIS_DIR/expect_scripts/timezone.exp

# Install packages for web server

sudo apt-get install apache2 apache2-utils libapache2-mod-python libapache2-mod-php5 php5 php5-mcrypt php5-sqlite php-symfony-yaml -y

# Install packages for feh, the photo program

sudo apt-get install libcurl4-openssl-dev libx11-dev libxt-dev libimlib2-dev libxinerama-dev libexif-dev libjpeg-progs -y


# Install feh and assorted tools

wget http://feh.finalrewind.org/feh-2.18.1.tar.bz2 -O ~/feh.tar.bz2 

pushd
cd ~
mkdir feh
tar -xjf feh.tar.bz2 -C feh --strip-components 1
cd feh
sed -i 's/exif ?= 0/exif ?= 1\nstat64 ?= 1/' config.mk 
make
sudo make install
cd ~
rm -rf feh
rm feh.tar.bz2
popd

# Disable screen blanking
sudo sed -i 's/#xserver-command=X/xserver-command=X -s 0 -dpms/' /etc/lightdm/lightdm.conf

sudo bash $THIS_DIR/serverInstall.sh

sudo bash $THIS_DIR/pyInstall.sh

sudo bash $THIS_DIR/populateDB.sh

sudo bash $THIS_DIR/cronInstall.sh
