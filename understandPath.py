#! /usr/bin/python

import sys
import os

inPath = sys.argv[1]
print inPath

isdir = os.path.isdir(inPath)
isabsdir = os.path.isabs(inPath)

print 'Is dir: ' + str(os.path.isdir(inPath))
print 'Is abs dir: ' + str(os.path.isabs(inPath))

if not isabsdir:
    inPath = os.path.expanduser(inPath)
    inPath = os.path.abspath(inPath)

print inPath