#! /bin/bash

RUN_DIR=init
PATH=$PATH:$RUN_DIR
CUR_DIR=`dirname $0`
echo $CUR_DIR

perl $CUR_DIR/$RUN_DIR/updateDatabase.pl
