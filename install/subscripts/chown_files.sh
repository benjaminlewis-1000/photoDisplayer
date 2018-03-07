#! /bin/bash

ONE_DIR_UP="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"

for i in `find $PROJECT_ROOT_DIR -name *out`; do chown pi $i; chmod 777 $i; done
for i in `find $PROJECT_ROOT_DIR -name *db` ; do chown pi $i; chmod 777 $i; done
