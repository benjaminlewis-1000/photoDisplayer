#! /bin/bash

PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

perl $PROJECT_ROOT_DIR/pyInit/database_create.pl

python addPics.py --addRoot
CONTINUE=1
