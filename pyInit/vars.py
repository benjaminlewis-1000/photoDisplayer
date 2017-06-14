#! /usr/bin/env python

from sys import platform as _platform

linuxType = 'Linux'
winType = 'Windows'
macType = 'Mac'


if _platform == "linux" or _platform == "linux2":
    osType = linuxType
    otherOStype = winType
elif _platform == "darwin":
    osType = macType
elif _platform == "win32":
    osType = winType
    otherOStype = linuxType


undefDirVal = "None"