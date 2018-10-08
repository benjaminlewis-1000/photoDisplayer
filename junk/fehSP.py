#! /usr/bin/env python

import os
import subprocess
from subprocess import PIPE
from time import sleep

disp_exe = subprocess.Popen(['/usr/local/bin/feh'] + ['-FxZNzY', '-D 4', '-f', '/app/ssList.tmp'], stderr=PIPE, stdout=PIPE )

for sl in iter(disp_exe.stderr.readline, ""):
	print sl
	if "X Error of failed request" in sl:
		disp_exe = subprocess.Popen(['/usr/local/bin/feh'] + ['-FxZNzY', '-D 4', '-f', '/app/ssList.tmp'], stderr=PIPE, stdout=PIPE )


print "hi"
