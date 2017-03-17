#! /usr/bin/python

import SimpleHTTPServer
import SocketServer
import geopy
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

import unicodedata

from geopy.geocoders import Nominatim
geolocator = Nominatim()

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer(("localhost", 8000),
                            requestHandler=RequestHandler)
server.register_introspection_functions()


def geoLookup(lat, lon):
    location = geolocator.reverse(str(lat) + ', ' + str(lon))

    house_number = '-'
    road = '-'
    city = '-'
    state = '-'
    postcode = '-'
    country = '-'

    if (not 'error' in location.raw):
        if ('house_number' in location.raw['address']):
            house_number = location.raw['address']['house_number']
        if ('road' in location.raw['address']):
            road = location.raw['address']['road']
        if ('city' in location.raw['address']):
            city = location.raw['address']['city']
        if ('village' in location.raw['address']):
            city = location.raw['address']['village']
        if ('state' in location.raw['address']):
            state = location.raw['address']['state']
        if ('postcode' in location.raw['address']):
            postcode = location.raw['address']['postcode']
        if ('country' in location.raw['address']):
            country = location.raw['address']['country']

    retJSON = '{' + \
              '"house_number" : "' + house_number  + \
              '", "road" : "' +  road + \
              '", "city" : "' + city  + \
              '", "state" : "' +  state + \
              '", "postcode" : "' + postcode  + \
              '", "country" : "' + country  + \
              '"}'

    if ('error' in location.raw):
        return retJSON
    else:
        return retJSON
server.register_function(geoLookup, 'geoLookup')

def test():
	return "hello world"
server.register_function(test)


# Run the server's main loop
server.serve_forever()