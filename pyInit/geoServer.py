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
import psutil
from subprocess import Popen
import re


import unicodedata

# from geopy.geocoders import Nominatim
# geolocator = Nominatim()

use_googmaps = True

import googlemaps
apikey = 'AIzaSyDN9_gjt7PDqWt8Jkwo-7AoT7Lyuz_Lsz0'
gmaps=googlemaps.Client(key=apikey)

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

assert len(sys.argv) > 1
assert sys.argv[1]
# print sys.argv[1]
assert float(sys.argv[1]) - int(sys.argv[1]) == 0

port = int(sys.argv[1])

# Create server
server = SimpleXMLRPCServer(("localhost", port),
                            requestHandler=RequestHandler)
server.register_introspection_functions()

locationDict = {}

def do_geocode(address, use_googmaps):
    if use_googmaps:
        try:
            value = gmaps.reverse_geocode(address)
            return value[0]['address_components']
        except Exception as e:
            print e
            print "Error: unknown"
            return -1
    else:
        ## Recursive until we get an answer
        try:
            return geolocator.reverse(address, timeout=3)
        except GeocoderTimedOut:

            sleep(1)
            print("Error: geocode timed out")
            try:
                value = gmaps.reverse_geocode(address)
                return value[0]['address_components']
            except Exception as e:
                print e
                print "Error: unknown"
                return -1

def geoLookup(lat, lon):

    use_googmaps = True

    gpsTuple = (lat,lon)

    if (gpsTuple in locationDict):
        print 'Already in location dict!'
        return locationDict[gpsTuple]

    # Prevent ourselves from getting throttled.
    # sleep(3)
    # Can't do this, it causes a timeout

    if use_googmaps:
        location = do_geocode(gpsTuple, use_googmaps)
    else:
        location = do_geocode(str(lat) + ', ' + str(lon))

    if location == -1:
        return -1

    print "Found something new"

    # print location.raw['address']

    house_number = '-'
    road = '-'
    city = '-'
    state = '-'
    postcode = '-'
    country = '-'

    if use_googmaps:
        for i in range(len(location)):
            if 'street_number' in location[i]['types']:
                house_number = location[i]['long_name']
            if 'route' in location[i]['types']:
                road = location[i]['long_name']
            if 'locality' in location[i]['types']:
                city = location[i]['long_name']
            if 'administrative_area_level_1' in location[i]['types']:
                state = location[i]['long_name']
            if 'postal_code' in location[i]['types']:
                postcode = location[i]['long_name']
            if 'country' in location[i]['types']:
                country = location[i]['long_name']
    else:
        if (not 'error' in location.raw):
            # print 'hafe'
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
