#! /usr/bin/python

import SimpleHTTPServer
import SocketServer
import geopy
from geopy.exc import GeocoderTimedOut
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import sys
import numbers
from time import sleep
import json

import unicodedata

from geopy.geocoders import Nominatim
geolocator = Nominatim()

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

assert len(sys.argv) > 1
assert sys.argv[1]
# print sys.argv[1]
assert float(sys.argv[1]) - int(sys.argv[1]) == 0


# Create server
server = SimpleXMLRPCServer(("localhost", int(sys.argv[1])),
                            requestHandler=RequestHandler)
server.register_introspection_functions()

locationDict = {}

def do_geocode(address):
    # Recursive until we get an answer
    try:
        return geolocator.reverse(address, timeout=3)
    except GeocoderTimedOut:
        sleep(1)
        print("Error: geocode timed out")
        return do_geocode(address)

def geoLookup(lat, lon):

    gpsTuple = (lat,lon)

    if (gpsTuple in locationDict):
        print 'Already in location dict!'
        return locationDict[gpsTuple]

    # Prevent ourselves from getting throttled.
    # sleep(3)

    location = do_geocode(str(lat) + ', ' + str(lon))

    print "Found something new"

    print location.raw['address']

    house_number = '-'
    road = '-'
    city = '-'
    state = '-'
    postcode = '-'
    country = '-'

    if (not 'error' in location.raw):
        print 'hafe'
        addr = location.raw['address']
        if ('house_number' in location.raw['address']):
            house_number = addr['house_number']
        if ('road' in addr):
            road = unicode(addr['road']).encode('utf-8')
        if ('city' in addr):
            city = unicode(addr['city']).encode('utf-8')
        if ('village' in addr):
            city = unicode(addr['village']).encode('utf-8')
        if ('state' in addr):
            state = unicode(addr['state']).encode('utf-8')
        if ('postcode' in  addr):
            postcode = unicode(addr['postcode']).encode('utf-8')
        if ('country' in addr):
            country = unicode(addr['country']).encode('utf-8')

    else:
        print "error!"

    retDict = {}
    retDict['house_number'] = house_number
    retDict['road'] = road
    retDict['city'] = city
    retDict['state'] = state
    retDict['postcode'] = postcode
    retDict['country'] = country

    retJSON = json.dumps(retDict)

    # retJSON = '{' + \
    #           '"house_number" : "' + house_number  + \
    #           '", "road" : "' +  road + \
    #           '", "city" : "' + city  + \
    #           '", "state" : "' +  state + \
    #           '", "postcode" : "' + postcode  + \
    #           '", "country" : "' + country  + \
    #           '"}'
    print retJSON
              
    locationDict[gpsTuple] = retJSON

    return retJSON

server.register_function(geoLookup, 'geoLookup')

def test():
	return "hello world"
server.register_function(test)


# Run the server's main loop
server.serve_forever()