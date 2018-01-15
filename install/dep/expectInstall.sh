#! /bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INSTALL_ROOT_DIR=$THIS_DIR #"$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"

# A few scripts to go and set some parameters on the Raspberry Pi
sudo expect $INSTALL_ROOT_DIR/expect_scripts/ssh.exp
sudo expect $INSTALL_ROOT_DIR/expect_scripts/boot.exp
sudo expect $INSTALL_ROOT_DIR/expect_scripts/timezone.exp

