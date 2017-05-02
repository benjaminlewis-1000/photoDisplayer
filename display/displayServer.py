#! /usr/bin/env python

import sys
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import yaml
import sqlite3
import os
import sys
import re
import random
import subprocess
from time import sleep
import json
import calendar

if len(sys.argv) > 1:
    debug = 1
else:
    debug = 0

#### Get our root path
rootDir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

### Load the parameters from files
with open(rootDir + '/config/serverParams.yaml') as stream:
    try:
        serverParams = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

with open(rootDir + '/config/params.yaml') as stream:
    try:
        appParams = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

### Determine that we are on linux
osRegex = re.search('.*nux.?', sys.platform)
# currentOS
if (osRegex == None): # Windows
    osRegex = re.search('.*win.?', sys.platform)
    if (osRegex.group(0)):
        currentOS = appParams['windowsType']
    else:
        # MAC, not defined
        currentOS = 0
else:
    currentOS = appParams['linuxType']


######### Set up the actual server #####################################

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/',)

# Create server

class displayServer:

    def __init__(self):
        self.server = SimpleXMLRPCServer(("127.0.0.1", serverParams['displayServerPort']),
                                    requestHandler=RequestHandler)
        self.server.register_introspection_functions()
    ###### Slideshow function, avaliable as server call

    def startSlideshow(self, criteriaJSON):
        ## Assume that we're only passing vetted JSON to the server here. 
        print criteriaJSON

        f = open('queryTest.out', 'w+')

        criteriaJSON = '''[{"num":0,"criteriaType":"Year","booleanValue":"is","criteriaVal":"2018"},{"num":3,"criteriaType":"Year","booleanValue":"is","criteriaVal":"2013"},{"num":1,"criteriaType":"Date%20Range","booleanValue":"04/12/2017","criteriaVal":"04/21/2017"},{"num":2,"criteriaType":"Person","booleanValue":"is","criteriaVal":"Benjamin Lewis"},{"num":5,"criteriaType":"Person","booleanValue":"is","criteriaVal":"Jessica Lewis"},{"num":3,"criteriaType":"Month","booleanValue":"is","criteriaVal":"October"}]'''
        val2 = '''[{"criteriaType":"Date Range","booleanValue":"","criteriaVal":""},{"criteriaType":"Date Range","booleanValue":"","criteriaVal":""}]'''

        slideshowParams = json.loads(criteriaJSON)

        # Build year limits

        for i in range(len(slideshowParams)):
            # print slideshowParams[i]
            paramType = slideshowParams[i]['criteriaType']
            start_Limit = slideshowParams[i]['booleanValue']
            end_Criteria = slideshowParams[i]['criteriaVal']

        people = ("Benjamin Lewis", "Jessica Lewis")
        year = (2016,)
        selectedMonth = {'March' : 'is', 'October' :'is not'}

        ### OR SQL person query
        orPersonQuery = '''SELECT photo AS c FROM photoLinker WHERE person = (SELECT people_key FROM people WHERE person_name = '''
        for i in range(len(people)):
            orPersonQuery += "\"" + people[i] + "\""
            if i != len(people) - 1:
                orPersonQuery += ''' ) UNION SELECT photo AS c FROM photoLinker WHERE person = (SELECT people_key FROM people WHERE person_name = '''

        orPersonQuery += " )"
        print >>f, orPersonQuery

        ## The only difference between AND and OR is INTERSECT vs UNION

        ### AND SQL person query
        ## SELECT * FROM photos AS photo_table_var JOIN (SELECT photo AS photo_key FROM photolinker WHERE person = 1 INTERSECT SELECT photo AS photo_key FROM photolinker WHERE person = 2 ) AS linker_tmp_var ON photo_table_var.photo_key = linker_tmp_var.photo_key
        andPersonQuery = '''SELECT photo_key FROM photos AS photo_key_and_var JOIN (SELECT photo AS photo_key FROM photoLinker WHERE person = '''
        for i in range(len(people)):
            personIntermediateQuery = '''(SELECT people_key FROM people WHERE person_name = "'''  + people[i]  + "\" )"
            andPersonQuery += personIntermediateQuery
            if i != len(people) - 1:
                andPersonQuery += ''' INTERSECT SELECT photo AS photo_key FROM photoLinker WHERE person = '''

        andPersonQuery += " ) AS linker_tmp_var ON photo_key_and_var.photo_key = linker_tmp_var.photo_key"
        print >>f, andPersonQuery


        ### Month SQL Query - each month should be unioned, then intersected with the larger query. 
        orMonthQuery = '''SELECT photo_key FROM Photos WHERE taken_month '''
        months = {"January" : 1, "February" : 2, "March" : 3, "April" : 4, "May" : 5, "June" : 6, "July" : 7, "August" : 8, "September" : 9, "October" : 10, "November" : 11, "December" : 12}
        i = 0
        for keyname in selectedMonth.keys():
            monthOrdinal = months[keyname]
            isOrIsnt = selectedMonth[keyname]
            if isOrIsnt == 'is':
                orMonthQuery += '= '
            else:
                orMonthQuery += '!= '
            orMonthQuery +=  str(monthOrdinal)
            if i != len(selectedMonth) - 1:
                orMonthQuery += " OR taken_month "
            i += 1


        #### Preliminary:
        prelimQuery = '''WITH photo_handle AS (SELECT * FROM Photos)'''
        prelimQuery += '''\n   SELECT * FROM photo_handle WHERE photo_key IN \n   '''

        prelimQuery += "(" + orPersonQuery + " INTERSECT " + orMonthQuery + ")"  # + andPersonQuery 

        print >>f, prelimQuery


        ### Connect to the database
        conn = sqlite3.connect(rootDir + "/databases/" + appParams['database'])
        conn.text_factory = str  # For UTF-8 compatibility
        c = conn.cursor()


        return serverParams['successVal']

    def run(self):
        self.server.register_function(self.startSlideshow, 'startSlideshow')
        self.server.serve_forever()



print "ready..."


if __name__ == '__main__':

    # Run the server's main loop
    myServer = displayServer();
    myServer.run()