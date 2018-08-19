
# FROM python:2.7-slim-stretch 
FROM darwish/libcec-rpi
# Get a Debian stretch image with python

ADD requirements.txt /

RUN apt-get update

RUN apt-get install iputils-ping -y --no-install-recommends

RUN apt-get install wget -y --no-install-recommends
    
RUN apt-get install gcc -y
RUN apt-get install -y python-pip 

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
RUN apt-get install build-essential -y --no-install-recommends 
RUN apt-get install python-all-dev -y --no-install-recommends
RUN apt-get install libexiv2-dev -y --no-install-recommends
RUN apt-get install libboost-python-dev -y --no-install-recommends
RUN apt-get install python-dev -y --no-install-recommends

RUN apt-get install exiv2 -y --no-install-recommends
RUN apt-get install python-pyexiv2 -y --no-install-recommends
# RUN apt-get install python-psutil -y --no-install-recommends
# RUN apt-get install python3-psutil -y --no-install-recommends
RUN apt-get install python-dateutil -y --no-install-recommends

# RUN cp /usr/lib/python2.7/dist-packages/libexiv2python.so /usr/lib/python2.7/dist-packages/pyexiv2
# RUN cp /usr/lib/python2.7/dist-packages/* /usr/lib/python2.7/ -r


ENV PYTHONPATH /usr/lib/python2.7/dist-packages/

# Clean up after apt-get installs 

RUN apt-get install  tk-dev  -y

EXPOSE 8040
RUN apt-get install nmap -y
# RUN rm -rf /var/lib/apt/lists/*

# Install exiftran for rotations

RUN apt-get install exiftran -y

RUN apt-get install apt-utils -y

RUN apt-get install sudo -y

