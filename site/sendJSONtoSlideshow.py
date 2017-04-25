#! /usr/bin/env python

json = argv[1]

print json

with open('jTest.out', 'a') as log:
    print >>log, json