#! /usr/bin/python

import xmlrpclib
import json

# port = raw_input()
port = 8040

# As a client, I have to know the IP address to which I am connecting. For now, 172.17.0.1 seems to be the gateway for the Docker bridge network.
# This gateway trick, however, only works when the port is exposed to the host. If the host is not aware of the docker port, you have to request the IP of the other container specifically (and it better be on the same network.)
s = xmlrpclib.ServerProxy('http://172.17.0.1:{}/RPC2'.format(port))
s = xmlrpclib.ServerProxy('http://fred:{}/RPC2'.format(port))
s = xmlrpclib.ServerProxy('http://localhost:{}/RPC2'.format(port))
# s = xmlrpclib.ServerProxy('http://0.0.0.0:{}/RPC2'.format(port))

rval =  s.geoLookup("40", "84")
print rval
# parsed_rval = json.loads(rval)
# print(parsed_rval['display_name'])
pj = json.loads(rval)

aDict = s.geoStringStandardize('Provo UT')

print aDict


# Print list of available methods
# print s.system.listMethods()
