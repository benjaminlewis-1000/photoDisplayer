#! /usr/bin/python

import xmlrpclib
import json

s = xmlrpclib.ServerProxy('http://localhost:8000')


rval =  s.geoLookup("40 deg N", "84 deg W")
print rval
# parsed_rval = json.loads(rval)
# print(parsed_rval['display_name'])
pj = json.loads(rval)



# Print list of available methods
# print s.system.listMethods()
