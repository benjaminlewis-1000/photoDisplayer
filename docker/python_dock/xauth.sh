#! /bin/bash

XSOCK="/tmp/.X11-unix"
XAUTH="/tmp/.docker.xauth"

echo $XAUTH
echo $XSOCK

export XSOCK
export XAUTH
xauth nlist :0 | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -

