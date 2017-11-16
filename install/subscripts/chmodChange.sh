#! /bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"

chmod 777 $PROJECT_ROOT_DIR/site
chmod 777 $PROJECT_ROOT_DIR/site/scripts_controlpanel
