#! /usr/bin/env python

# geoTextToLocation.py
# Given a text input, get the GPS coordinates and a standardized 
# textual representation of the data.

# import geopy
# from geopy.geocoders import Nominatim
# import pygeohash

import googlemaps


def stringToStandard(location_string):

    apikey = 'AIzaSyDN9_gjt7PDqWt8Jkwo-7AoT7Lyuz_Lsz0'
    # apikey = 'AIzaSyBN6RKzo16vf8kMDgDw_AjmOLFU3HRZtBo'
    gmaps=googlemaps.Client(key=apikey)
    value = gmaps.geocode(location)

    components = value[0]['address_components']

    location_types = (map( lambda array: list(set(array['types']) - set(['political']))[0], components))
    location_values = (map( lambda array: array['long_name'], components))

    lat = value[0]['geometry']['location']['lat']
    lon = value[0]['geometry']['location']['lng']

    addressDict = {}
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
        if ad['house_number'] != '':
            builtString += ad['house_number'] + ' '
        if ad['road'] != '':
            builtString += ad['road'] + ', '
        if ad['city'] != '':
            builtString += ad['city'] + ', '
        if ad['state'] != '':
            builtString += ad['state'] + ', '
        if ad['country'] != '':
            builtString += ad['country']
        print builtString
        addressDict['string'] = builtString

    addToDict('street_number', 'house_number')
    addToDict('route', 'road')
    addToDict('locality', 'city')
    addToDict('administrative_area_level_1', 'state')
    addToDict('country', 'country')

    dictToString()
    print addressDict

    return addressDict

location = raw_input()
stringToStandard(location)