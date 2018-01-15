#! /bin/bash

read -p "Would you like to set the Lewis-family only ddns server? " 
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
	INSTALL_DDNS=1
else
	INSTALL_DDNS=0
fi

echo $INSTALL_DDNS

if [[ $INSTALL_DDNS ]]; then
	echo 'hi'

fi
