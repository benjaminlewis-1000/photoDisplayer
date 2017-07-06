#! /bin/bash

PIDS=`ps ax | grep geoServer.py | grep -v grep |awk '{print $1}'`

for i in $PIDS;
  do echo $i;
  kill -9 $i
done
