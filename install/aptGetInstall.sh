#! /bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

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
