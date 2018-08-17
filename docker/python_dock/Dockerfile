
# FROM python:2.7-slim-stretch 
# FROM resin/rpi-raspbian
FROM darwish/libcec-rpi
# Get a Debian stretch image with python

ADD requirements.txt /

RUN apt-get update

RUN apt-get install iputils-ping -y --no-install-recommends

RUN apt-get install wget -y --no-install-recommends
    
RUN apt-get install gcc -y
#RUN apt-get install -y python-pip 

RUN apt-get install python-pip -y
RUN apt-get install python-dev python3-dev -y

RUN pip install -r /requirements.txt 

# RUN apt-get install python-psutil python3-psutil python-dateutil -y

# yes | sudo cpan install DBI
# sudo cpan install XML::Simple
# sudo cpan install DBD::SQLite

# Install CEC packages - these let you, in theory, control the TV from the computer.

# RUN apt-get install libcec4 -y --no-install-recommends
# RUN apt-get install cec-utils -y --no-install-recommends

# Install Expect scripting - allows us to use GUIs automatically 

RUN apt-get install expect -y --no-install-recommends

RUN apt-get install xinput -y --no-install-recommends


# Install packages for feh, the photo program

RUN apt-get install libcurl4-openssl-dev -y --no-install-recommends
RUN apt-get install libx11-dev -y --no-install-recommends
RUN apt-get install libxt-dev -y --no-install-recommends
RUN apt-get install libimlib2-dev -y --no-install-recommends
RUN apt-get install libxinerama-dev -y --no-install-recommends
RUN apt-get install libexif-dev -y --no-install-recommends
RUN apt-get install libjpeg-progs -y --no-install-recommends


RUN apt-get install imagemagick -y --no-install-recommends

RUN apt-get install make -y --no-install-recommends

# Imlib2 for feh
RUN apt-get install libimlib2-dev

RUN apt-get install bzip2 -y --no-install-recommends

# RUN 

ENV DISPLAY :0

# Build dependencies for pyexiv2
RUN apt-get update
RUN apt-get install  build-essential git cmake libudev-dev libxrandr-dev python-dev pkg-config libraspberrypi0 -y
RUN apt-get install  libraspberrypi-dev libraspberrypi-doc libraspberrypi-bin -y
RUN apt-get install python-tk

ADD cronjobs.txt /etc/cron.d/userCron
RUN chmod 0644 /etc/cron.d/userCron
RUN echo "PYTHONPATH=${PYTHONPATH}:/usr/lib/python2.7/dist-packages" >> /etc/profile
RUN chmod +x /etc/cron.d/userCron

# RUN export PYTHONPATH="${PYTHONPATH}:/usr/lib/python2.7/dist-packages"
# RUN apt-get install liblockdev1-dev swig -y

# RUN git clone https://github.com/Pulse-Eight/platform.git
# RUN mkdir platform/build && cd platform/build
# RUN cmake .. && make && make install
# RUN cd ../..

# RUN git clone https://github.com/Pulse-Eight/libcec.git
# WORKDIR /libcec
# RUN git submodule update --init
# WORKDIR src/platform
# RUN mkdir build && cd build && cmake .. && make -j4 && make install
# WORKDIR /libcec 

# run mkdir build && cd build && cmake cmake --DRPI_INCLUDE_DIR=/opt/vc/include -DRPI_LIB_DIR=/opt/vc/lib -DCMAKE_INSTALL_PREFIX=/opt/libcec .. && make -j4 && make install
# ENV LD_LIBRARY_PATH="/opt/libcec/lib"
# ENV PATH="/opt/libcec/bin:${PATH}"

USER developer
ENV HOME /home/developer

# RUN echo "* * * * * python /app/pyInit/addPics.py" | crontab -

MAINTAINER Benjamin Lewis
# Need to put the ENTRYPOINT in shell mode, so that it will open in a shell.
ENTRYPOINT  bash /app/scripts/dockerStart.sh && /bin/bash
#RUN useradd -G sudo -u 1000 --create-home emacs

#ENV HOME /home/emacs
#WORKDIR /home/emacs


############ sudo xhost local:root  && xhost +
#########  https://stackoverflow.com/questions/28392949/running-chromium-inside-docker-gtk-cannot-open-display-0
#########  http://fabiorehm.com/blog/2014/09/11/running-gui-apps-with-docker/

# RUN apt-get remove gcc bzip2 make expect wget -y

# RUN apt-get install vim -y --no-install-recommends
# RUN apt-get install nautilus -y --no-install-recommends

# RUN apt-get install aptitude -y --no-install-recommends
# RUN apt-get install libraspberrypi-dev -y


