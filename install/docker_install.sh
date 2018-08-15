#! /bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

bash $THIS_DIR/sshEnable.sh

sudo apt-get update -y

sudo apt-get upgrade -y

# Install dependencies for Docker
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common -y

# Add docker's key
# Instructions: https://howchoo.com
curl -fsSL https://yum.dockerproject.org/gpg | sudo apt-key add -

# sudo apt-key fingerprint 0EBFCD88

# Add the docker repository
# sudo add-apt-repository "deb [arch=armhf] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo add-apt-repository \ 
   " deb https://apt.dockerproject.org/repo \
     raspbian-$(lsb_release -cs) \
     main" 

sudo echo "deb https://apt.dockerproject.org/repo raspbian-jessie main" >> /etc/apt/sources.list

sudo apt-get update -y

# Install docker
sudo apt-get install docker-engine -y

# Add user to docker group
sudo usermod -aG docker $USER

sudo apt-get install vim -y

# Change the docker-compose.yaml file
DOCKER_DIR=$PROJECT_ROOT_DIR/docker/python_dock

# Disable screen blanking
# Source: https://www.geeks3d.com/hacklab/20160108/how-to-disable-the-blank-screen-on-raspberry-pi-raspbian/
sudo sed -i 's/#xserver-command=X/xserver-command=X -s 0 -dpms/' /etc/lightdm/lightdm.conf
sudo sed -i 's/# xserver-command=X/xserver-command=X -s 0 -dpms/' /etc/lightdm/lightdm.conf

sudo service lightdm restart

pushd .

cd $DOCKER_DIR

sudo docker build -t photodisplay .

cp docker-compose-template.yaml docker-compose.yaml

PI_PHOTO_DIR=/mnt/photos
sudo mkdir -p $PI_PHOTO_DIR

sed -i "s|THIS_DIR|${PROJECT_ROOT_DIR}|" docker-compose.yaml
sed -i "s|PHOTO_DIR|${PI_PHOTO_DIR}|" docker-compose.yaml
sed -i "s| /|/|g" docker-compose.yaml
sed -i "s|-/|- /|g" docker-compose.yaml

popd

sudo apt-get install docker-compose -y

# Mount the filesystem
sudo apt-get install cifs-utils
echo "//192.168.1.15/server_share /mnt/photos cifs user=benjamin,pass=lewis,uid=1000,iocharset=utf8 0 0" | sudo tee -a /etc/fstab 


sudo reboot
