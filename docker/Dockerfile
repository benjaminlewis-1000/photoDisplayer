
FROM python:2.7-slim-stretch 
# Get a Debian stretch image with python

ADD requirements.txt /

RUN apt-get update

RUN apt-get install wget -y

RUN apt-get install iputils-ping -y

RUN apt-get install gcc -y
# RUN apt-get install -y python-pip 

RUN pip install -r requirements.txt 

# RUN apt-get install python-psutil python3-psutil python-dateutil -y

# yes | sudo cpan install DBI
# sudo cpan install XML::Simple
# sudo cpan install DBD::SQLite

RUN apt-get install vim -y
RUN apt-get install nautilus -y

RUN apt-get install aptitude -y

# Install CEC packages - these let you, in theory, control the TV from the computer.

RUN apt-get install libcec4 -y
RUN apt-get install cec-utils -y

# Install Expect scripting - allows us to use GUIs automatically 

RUN apt-get install expect -y

RUN apt-get install xinput -y


# Install packages for feh, the photo program

RUN apt-get install libcurl4-openssl-dev -y
RUN apt-get install libx11-dev -y
RUN apt-get install libxt-dev -y
RUN apt-get install libimlib2-dev -y
RUN apt-get install libxinerama-dev -y
RUN apt-get install libexif-dev -y
RUN apt-get install libjpeg-progs -y

# NTFS filesystem
RUN apt-get install ntfs-3g -y

RUN apt-get install imagemagick -y

RUN apt-get install make -y

RUN wget http://feh.finalrewind.org/feh-2.18.1.tar.bz2 -O /feh.tar.bz2

RUN mkdir feh
RUN tar -xjf /feh.tar.bz2 -C feh --strip-components 1
RUN cd feh
RUN sed -i 's/exif ?= 0/exif ?= 1\nstat64 ?= 1/' /feh/config.mk
RUN make -C /feh -j9
RUN make install -C /feh
RUN rm -rf feh
RUN rm feh.tar.bz2

ENV DISPLAY :0

# Build dependencies for pyexiv2
RUN apt-get install build-essential -y
RUN apt-get install python-all-dev -y
RUN apt-get install libexiv2-dev -y
RUN apt-get install libboost-python-dev -y
RUN apt-get install python-dev -y

RUN apt-get install exiv2 -y
RUN apt-get install python-pyexiv2 -y
# RUN apt-get install python-psutil -y
# RUN apt-get install python3-psutil -y
RUN apt-get install python-dateutil -y

# RUN cp /usr/lib/python2.7/dist-packages/libexiv2python.so /usr/lib/python2.7/dist-packages/pyexiv2
# RUN cp /usr/lib/python2.7/dist-packages/* /usr/lib/python2.7/ -r

ENV PYTHONPATH /usr/lib/python2.7/dist-packages/

# RUN apt-get install libraspberrypi-dev -y


# Install packages for web server

# RUN apt-get install apache2 -y
# RUN apt-get install apache2-utils -y
# RUN apt-get install libapache2-mod-python -y
# RUN apt-get install libapache2-mod-php5 -y
# RUN apt-get install php5 -y
# RUN apt-get install php5-mcrypt -y
# RUN apt-get install php5-sqlite -y
# RUN apt-get install php-symfony-yaml -y
# RUN apt-get install php-sqlite3 -y
# RUN apt-get install php-xmlrpc -y
# RUN apt-get install libapache2-mod-php -y
# RUN apt-get install php -y