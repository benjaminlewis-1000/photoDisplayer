#! /usr/bin/env python

from time import gmtime, strftime

currentTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
logfile = open('testPy.out', 'a')
print >>logfile, currentTime
logfile.close()