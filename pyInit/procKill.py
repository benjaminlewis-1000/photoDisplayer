#! /usr/bin/env python

import psutil
from subprocess import Popen
import re

for process in psutil.process_iter():
    # print process.cmdline
    cmdline = process.cmdline
    if re.search(r'geoServer', str(cmdline) ) :
        print('Process found. Terminating it.')
        print process.cmdline
        if str(8040) in cmdline:
            print "really found it"
        process.terminate()
        break
