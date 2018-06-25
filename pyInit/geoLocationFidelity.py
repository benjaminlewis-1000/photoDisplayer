#! /usr/bin/env python

# geoTextToLocation.py
# Given a text input, get the GPS coordinates and a standardized 
# textual representation of the data.

# import geopy
# from geopy.geocoders import Nominatim
# import pygeohash

import googlemaps
import json

def stringToStandard(location_string):

    apikey = 'AIzaSyDN9_gjt7PDqWt8Jkwo-7AoT7Lyuz_Lsz0'
    # apikey = 'AIzaSyBN6RKzo16vf8kMDgDw_AjmOLFU3HRZtBo'
    gmaps=googlemaps.Client(key=apikey)
    value = gmaps.geocode(location_string)

    addressDict = {}

    if len(value) == 0:
        print "aha"
        addressDict['validity'] = False
        return json.dumps(addressDict)
    else:
        addressDict['validity'] = True

    components = value[0]['address_components']

    location_types = (map( lambda array: list(set(array['types']) - set(['political']))[0], components))
    location_values = (map( lambda array: array['long_name'], components))

    lat = value[0]['geometry']['location']['lat']
    lon = value[0]['geometry']['location']['lng']

    addressDict['latitude'] = lat
    addressDict['longitude'] = lon

    def addToDict(desiredLocType, synonym):
        if desiredLocType in location_types:
            index = location_types.index(desiredLocType)
            value = location_values[index]
            addressDict[synonym] = value
        else:
            addressDict[synonym] = ''

    def dictToString():
        builtString = ''
        ad = addressDict
        bestFidelity = 'number'

        if ad['house_number'] != '':
            builtString += ad['house_number'] + ' '
        else:
            bestFidelity = 'road'
        if ad['road'] != '':
            builtString += ad['road'] + ', '
        else:
            bestFidelity = 'city'
        if ad['city'] != '':
            builtString += ad['city'] + ', '
        else:
            bestFidelity = 'state'
        if ad['state'] != '':
            builtString += ad['state'] + ', '
        else:
            bestFidelity = 'country'
        if ad['country'] != '':
            builtString += ad['country']
        # print builtString
        addressDict['string'] = builtString
        addressDict['best_fidelity'] = bestFidelity

    addToDict('street_number', 'house_number')
    addToDict('route', 'road')
    addToDict('locality', 'city')
    addToDict('administrative_area_level_1', 'state')
    addToDict('country', 'country')

    dictToString()
    return json.dumps(addressDict)

if __name__ == "__main__":
    location = raw_input()
    locationDict = stringToStandard(location)
    print locationDict
