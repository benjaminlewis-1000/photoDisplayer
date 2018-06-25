#! /bin/bash

PHOTODISPLAY_ROOT='/home/lewis/gitRepos/photoDisplayer'

GEOSERVER_NAME='geoServer'

docker run -p 8040:8040 --name $GEOSERVER_NAME --hostname $GEOSERVER_NAME -v $PHOTODISPLAY_ROOT:/usr/src/app -w /usr/src/app -v $HOME:/root --network bridge --rm -d photodisplay python pyInit/geoServer.py 8040 

docker run -e GEOSERVER_NAME=$GEOSERVER_NAME --name webserver --link $GEOSERVER_NAME -it -p 80:80 -v $PHOTODISPLAY_ROOT/site/:/var/www/html -v $PHOTODISPLAY_ROOT:/var/www -v /etc/timezone:/etc/timezone -d --rm webserver 
