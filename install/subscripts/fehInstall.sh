#! /bin/bash

# Install feh and assorted tools
wget http://feh.finalrewind.org/feh-2.18.1.tar.bz2 -O ~/feh.tar.bz2 
# test 2
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