#! /usr/bin/env python

import xmlrpclib
import os
import xmltodict
import sqlite3
import sys

assert len(sys.argv) >= 2, 'not enough input arguments'

requestedShow = sys.argv[1]


#### Get our root path
rootDir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), ''))

with open(rootDir + '/config/params.xml') as stream:
    try:
        tparams = xmltodict.parse(stream.read())
    except Exception as exc:
        print(exc)
        exit(1)

## Connect to the display server
client = xmlrpclib.ServerProxy('http://127.0.0.1:' + tparams['params']['serverParams']['displayServerPort'] + '/')

# Obtain all of the parameters for the database where the website defines slideshows.
siteDatabasePath = os.path.join(rootDir, 'site', tparams['params']['websiteParams']['siteDBname'])
dbSchemaParams = tparams['params']['websiteParams']['siteDBschema']

showDefTableName = dbSchemaParams['slideshowDefTable']['name']
showNameCol = dbSchemaParams['slideshowDefTable']['showNameCol']
showJsonCol = dbSchemaParams['slideshowDefTable']['jsonCol']

print siteDatabasePath

getShowNamesQuery = '''SELECT {} FROM {}'''.format(showNameCol, showDefTableName)

conn = sqlite3.connect(siteDatabasePath)

c = conn.cursor()
c.execute(getShowNamesQuery)
fileResults = c.fetchall()
# Convert the results to a list
fileResults = [i[0] for i in fileResults]

requestInListOfShows = (unicode(requestedShow) in set(fileResults))

if requestInListOfShows:
    # Get the corresponding JSON:
    getShowJSON = '''SELECT {} FROM {} WHERE {} = "{}"'''.format(showJsonCol, showDefTableName, showNameCol, unicode(requestedShow))
    c.execute(getShowJSON)
    jsonResult = c.fetchall()[0][0]
else:
    # assert 1 == 0, "Need to implement a 'get all' function."
    jsonResult = '[{"num":0, "criteriaType":"All","booleanValue":"is", "criteriaVal":"all"}]'

# Pass the JSON request to the server

client.buildQuery(jsonResult)
