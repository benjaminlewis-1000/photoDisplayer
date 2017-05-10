#! /usr/bin/env python

import sys
import xmlrpclib
import datetime
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
import xmltodict

if len(sys.argv) > 1:
    debug = 1
else:
    debug = 0

#### Get our root path
rootDir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))



######### Set up the actual server #####################################

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/',)

# Create server

class displayServer:

    def __init__(self, xmlParams):
        self.server = SimpleXMLRPCServer(("127.0.0.1", int(xmlParams['params']['serverParams']['displayServerPort'])),
                                    requestHandler=RequestHandler)
        self.server.register_introspection_functions()

        self.commandString = "-FxZ -N -z -Y -D 2 --auto-rotate"

        self.masterQuery = ""

        self.xmlParams = xmlParams

        self.printDebug = False

        ### Connect to the database
        self.conn = sqlite3.connect(rootDir + "/databases/" + self.xmlParams['params']['photoDatabase']['fileName'])
        self.conn.text_factory = str  # For UTF-8 compatibility

        self.fileListName = '.slideshowFileList.txt'

        self.p = None

    ###### Slideshow function, avaliable as server call
    def setSlideshowProperties(self, propertiesJSON):
        ## Set properties, according to page https://linux.die.net/man/1/feh
        # Default, read from file | -f <filename>

        # Action   |  -A
        ## Set to zoom fully with no borders: 
        # Auto-Zoom    |   -Z
        # Borderless window  | -x
        # Fullscreen  | -F

        # Hide pointer  | -Y
        # Randomize     | -z
        # Delay (sec)   | -D (int)
        # Auto-rotate based on image data | --auto-rotate 
        # Show filename  | -d
        # No menus   | -N

        #### As-yet unexplored properties:
        # Quiet mode  | -q
        # Sort (with parameters) | -S <param> - name, filename, mtime, width, height, pixels, size, format. 
        # Stretch small images | -s

        #  "-YFxZNz", "-D", "2", "--auto-rotate", "-d",

        commandDict = {"fullZoom": " -ZxF", "hidePointer": " -Y", "randomize": " -z", "delay": " -D ", "autorotate": " --auto-rotate", \
                        "showFilename": " -d", "noMenus": " -N", "quiet": " -q", "sort": " -S ", "stretch": " -s"  }

        properties = json.loads(propertiesJSON)

        self.commandString = ""
        for i in range(len(properties)):
            propertyType = properties[i]['property']
            propertyVal = unicode(properties[i]['enabled'])
            assert propertyType in commandDict.keys()
            if propertyType.lower() == 'delay':
                try:
                    val = float(propertyVal)
                except:
                    print "Value for delay is not a float"
                assert val >= 0
                if val > 0:
                    # Let the maximum delay be 5 minutes.
                    self.commandString += commandDict['delay'] + str(min(val, 300.0))
            if propertyType.lower() == 'sort':
                assert propertyVal.lower() in ['0', 'none', 'name', 'filename', 'mtime', 'width', 'height', 'pixels', 'size', 'format']
                if propertyVal.lower() not in ['0', 'none']:
                    self.commandString += commandDict['sort'] + propertyVal.lower()
            if propertyType.lower() in ['fullZoom', 'hidePointer', 'randomize', 'autorotate', 'showFilename', 'noMenus', 'quiet', 'stretch']:
                assert propertyVal.isnumeric() or propertyVal.lower() in ['true', 'false']
                if propertyVal != 0:
                    self.commandString += commandDict[propertyType.lower()]

        # print self.commandString

    def startSlideshow(self):
        if currentOS != self.xmlParams['params']['ostypes']['linuxType']:
            raise Exception('The current OS is not supported as a slideshow type.')

        if os.path.isfile(self.fileListName):
            if self.p != None:
                self.p.terminate()
                self.p.wait()
            self.p = subprocess.Popen(["feh", self.commandString, "-f ", self.fileListName])
        else:
            raise Exception('File doesn\'t exist! This is solvable, I just haven\'t done it yet.')


    def buildQuery(self, criteriaJSON):
        ## Assume that we're only passing vetted JSON to the server here. 
        slideshowParams = json.loads(criteriaJSON)

        people = [ ]
        selectedYears = [ ]
        selectedMonths = [ ]
        dateRangeVals = [ ]

        for i in range(len(slideshowParams)):
            critType = slideshowParams[i]['criteriaType']
            boolVal = slideshowParams[i]['booleanValue']
            critVal = slideshowParams[i]['criteriaVal']
            if critType == 'Year':
                assert unicode(critVal).isnumeric()
                selectedYears.append( (critVal, boolVal) )
            if str(critType) == 'Date Range' or str(critType) == "Date%20Range":
                dateRangeVals.append( (boolVal, critVal) )
            if critType == 'Person':
                people.append(critVal)
            if critType == 'Month':
                selectedMonths.append( (critVal, boolVal) )
            if critType not in ['Year', 'Date Range', "Date%20Range", 'Person', 'Month']:
                raise TypeError

        # Build year limits

        for i in range(len(slideshowParams)):
            # print slideshowParams[i]
            paramType = slideshowParams[i]['criteriaType']
            start_Limit = slideshowParams[i]['booleanValue']
            end_Criteria = slideshowParams[i]['criteriaVal']

        photoLinkerTable =  self.xmlParams['params']['photoDatabase']['tables']['photoLinkerTable']
        plTableName      =  photoLinkerTable['Name']
        plPerson         =  photoLinkerTable['Columns']['linkerPeople']
        plPhoto          =  photoLinkerTable['Columns']['linkerPhoto']

        peopleTable   =  self.xmlParams['params']['photoDatabase']['tables']['peopleTable']
        ppTableName   =  peopleTable['Name']
        ppKey         =  peopleTable['Columns']['peopleKey']
        ppName        =  peopleTable['Columns']['personName']

        photosTable   =  self.xmlParams['params']['photoDatabase']['tables']['photoTable']
        phTableName   =  photosTable['Name']
        phKey         =  photosTable['Columns']['photoKey']
        phTableName   =  photosTable['Name']
        phTakenMonth  =  photosTable['Columns']['photoMonth']
        phTakenYear   =  photosTable['Columns']['photoYear']
        phTakenDate   =  photosTable['Columns']['photoDate']
        phTakenDate   =  photosTable['Columns']['photoDate']
        phFile        =  photosTable['Columns']['photoFile']
        phRootDir     =  photosTable['Columns']['rootDirNum']

        ### OR SQL person query
        # orPersonQuery = '''SELECT photo AS c FROM photoLinker WHERE person = (SELECT people_key FROM people WHERE person_name = '''
        orPersonQuery = '''SELECT {} AS c FROM {} WHERE {} = (SELECT {} FROM {} WHERE {} = '''.format(plPhoto, plTableName, plPerson, ppKey, ppTableName, ppName)
        for i in range(len(people)):
            orPersonQuery += "\"" + people[i] + "\""
            if i != len(people) - 1:
                ## orPersonQuery += ''' ) UNION SELECT photo AS c FROM photoLinker WHERE person = (SELECT people_key FROM people WHERE person_name = '''
                orPersonQuery += ''' ) UNION SELECT {} AS c FROM {} WHERE {} = (SELECT {} FROM {} WHERE {} = '''.format(plPhoto, plTableName, plPerson, ppKey, ppTableName, ppName)

        orPersonQuery += " )"

        ## The only difference between AND and OR is INTERSECT vs UNION

        ### AND SQL person query
        ## Example: SELECT * FROM photos AS photo_table_var JOIN (SELECT photo AS photo_key FROM photolinker WHERE person = 1 INTERSECT SELECT photo AS photo_key FROM photolinker WHERE person = 2 ) AS linker_tmp_var ON photo_table_var.photo_key = linker_tmp_var.photo_key

        ## andPersonQuery = '''SELECT photo_key FROM photos AS photo_key_and_var JOIN (SELECT photo AS photo_key FROM photoLinker WHERE person = '''
        andPersonQuery = '''SELECT {} FROM {} AS photo_key_and_var JOIN (SELECT {} AS {} FROM {} WHERE {} = '''.format(phKey, phTableName, plPhoto, phKey, plTableName, plPerson)
        for i in range(len(people)):
            ## personIntermediateQuery = '''(SELECT people_key FROM people WHERE person_name = "'''  + people[i]  + "\" )"
            personIntermediateQuery = '''(SELECT {} FROM {} WHERE {} = "'''.format(ppKey, ppTableName, ppName)  + people[i]  + "\" )"
            andPersonQuery += personIntermediateQuery
            if i != len(people) - 1:
                ## andPersonQuery += ''' INTERSECT SELECT photo AS photo_key FROM photoLinker WHERE person = '''
                andPersonQuery += ''' INTERSECT SELECT {} AS {} FROM {} WHERE {} = '''.format(plPhoto, phKey, plTableName, plPerson)

        andPersonQuery += " ) AS linker_tmp_var ON photo_key_and_var.{} = linker_tmp_var.{}".format(phKey, phKey)


        ### Month SQL Query - each month should be unioned, then intersected with the larger query. 
        ### ANDing month queries makes no sense - you can't have a photo that is in two months, and
        ### negating a month is superflous. 
        # orMonthQuery = '''SELECT photo_key FROM Photos WHERE taken_month '''
        orMonthQuery = '''SELECT {} FROM {} WHERE {} '''.format(phKey, phTableName, phTakenMonth)
        months = {"January" : 1, "February" : 2, "March" : 3, "April" : 4, "May" : 5, "June" : 6, "July" : 7, "August" : 8, "September" : 9, "October" : 10, "November" : 11, "December" : 12}
        i = 0
        for i in range(len(selectedMonths)):
            monthOrdinal = months[ selectedMonths[i][0] ]
            isOrIsnt = selectedMonths[i][1]
            if isOrIsnt == 'is':
                orMonthQuery += '= '
            else:
                orMonthQuery += '!= '
            orMonthQuery +=  str(monthOrdinal)
            if i != len(selectedMonths) - 1:
                orMonthQuery += " OR {} ".format(phTakenMonth)
            i += 1

        ### Similar with years - Anding them doesn't make sense for is/is not; 
        ### However, it does make sense with befores/afters.
        # orYearQuery = '''SELECT photo_key FROM photos WHERE taken_year '''
        # andYearQuery = '''SELECT photo_key FROM photos WHERE taken_year '''
        orYearQuery = '''SELECT {} FROM {} WHERE {} '''.format(phKey, phTableName, phTakenYear)
        andYearQuery = '''SELECT {} FROM {} WHERE {} '''.format(phKey, phTableName, phTakenYear)
        yearQueryStart = [False, False]
        andIndex = 0
        orIndex = 1

        for i in range(len(selectedYears)):
            year = selectedYears[i][0]
            modifier = selectedYears[i][1]
            if modifier.lower() in ['is before', 'is after']:
                if yearQueryStart[andIndex]:
                    andYearQuery += ' AND {} '.format(phTakenYear)
                if modifier.lower() == 'is before':
                    andYearQuery += ' < '
                else:
                    andYearQuery += ' > '
                andYearQuery += str(year)
                yearQueryStart[andIndex] = True
            elif modifier.lower() in ['is', 'is not']:
                if yearQueryStart[orIndex]:
                    orYearQuery += ' OR {} '.format(phTakenYear)
                if modifier.lower() == 'is':
                    orYearQuery += ' = '
                else:
                    orYearQuery += ' != '
                orYearQuery += str(year)
                yearQueryStart[orIndex] = True
            else:
                raise Exception('Year modifier is not valid.')

        ### Date ranges - must be or'd. It doesn't make sense to AND date ranges, because the date
        ### range could be changed or another date range selected to get the appropriate values. 
        orDateRangeQuery = '''SELECT {} FROM {} WHERE {} '''.format(phKey, phTableName, phTakenDate)
        for i in range(len(dateRangeVals)):
            startDate = dateRangeVals[i][0]
            endDate = dateRangeVals[i][1]
            startDate = datetime.datetime.strptime(startDate, "%m/%d/%Y").strftime("%Y-%m-%d 00:00:00")
            endDate = datetime.datetime.strptime(endDate, "%m/%d/%Y").strftime("%Y-%m-%d 23:59:59")
            orDateRangeQuery += " > \"" + startDate + "\" AND {} < \"".format(phTakenDate) + endDate + "\""
            if i != len(dateRangeVals) - 1:
                orDateRangeQuery += " OR {} ".format(phTakenDate)



        self.masterQuery = ""
        ### Build a query that encapsulates all of the date ranges and specifics that were requested. 
        buildDates = ""
        ## From (Year AND Month) OR DateRange
        if len(selectedYears) > 0:
            # UNION the year range with the individual years
            # (i.e. the andYearQuery with the orYearQuery) - but only if applicable.
            if yearQueryStart[andIndex] and yearQueryStart[orIndex]:
                buildDates += andYearQuery + " UNION " + orYearQuery + " "
            else:
                if yearQueryStart[andIndex]:
                    buildDates += andYearQuery
                if yearQueryStart[orIndex]:
                    buildDates += orYearQuery
        if len(selectedMonths) > 0:
            if buildDates != "":
                buildDates += " INTERSECT "
            buildDates += orMonthQuery
        if len(dateRangeVals) > 0:
            if buildDates != "":
                buildDates += " UNION "
            buildDates += orDateRangeQuery

        if buildDates != "":
            self.masterQuery += buildDates

        if orPersonQuery != "":
            self.masterQuery += " INTERSECT " + orPersonQuery

        if self.masterQuery != "":
            #### Preliminary:
            prelimQuery = '''SELECT {}, {}, {} FROM {} WHERE {} IN \n '''.format(phKey, phFile, phRootDir, phTableName, phKey)
            self.masterQuery = prelimQuery +  "(" +  self.masterQuery + ")"  

        if self.printDebug:
            with open('queryTest.out', 'w+') as f:
                print >>f, orPersonQuery
                print >>f, andPersonQuery
                print >>f, andYearQuery
                print >>f, orYearQuery
                print >>f, orDateRangeQuery
                print >>f, buildDates
                print >>f, self.masterQuery
        else:
            with open('queryTest.out', 'w+') as f:
                print >>f, self.masterQuery

        if self.masterQuery != "":
            c = self.conn.cursor()
            c.execute(self.masterQuery)
            fileResults = c.fetchall()

            rootTable =  self.xmlParams['params']['photoDatabase']['tables']['rootTable']
            rtName    =  rootTable['Name']
            rtKey     =  rootTable['Columns']['rootKey']

            if currentOS == self.xmlParams['params']['ostypes']['linuxType']:
                rtPath = rootTable['Columns']['linuxRootPath']
            else:
                rtPath = rootTable['Columns']['windowsRootPath']

            rootPathQuery = '''SELECT {}, {} FROM {}'''.format(rtKey, rtPath, rtName)
            c.execute(rootPathQuery)
            rootDirQueryResults = c.fetchall()

            rootDict = {}
            for i in range(len(rootDirQueryResults)):
                rootKey = rootDirQueryResults[i][0]
                rootPath = rootDirQueryResults[i][1]
                if rootPath == None:
                    raise Exception('Error! Root path for this OS is not defined. Please run updateDatabase.pl')
                ## Even though the root keys are integers, they should be mutually exclusive.
                assert rootKey not in rootDict.keys()
                rootDict[rootKey] = rootPath

            with open(self.fileListName, 'w') as file:
                for i in range(len(fileResults)):
                    photo_file = fileResults[i][1]
                    photo_root_key = fileResults[i][2]
                    print >>file, rootDict[photo_root_key] + photo_file

            self.startSlideshow()


        return self.xmlParams['params']['serverParams']['successVal']

    def run(self):
        self.server.register_function(self.startSlideshow, 'startSlideshow')
        self.server.register_function(self.setSlideshowProperties, 'setSlideshowProperties')
        self.server.register_function(self.buildQuery, 'buildQuery')
        self.server.serve_forever()




if __name__ == '__main__':
    ### Load the parameters from files

    with open('../config/params.xml') as stream:
        try:
            tparams = xmltodict.parse(stream.read())
        except Exception as exc:
            print(exc)
            exit(1)

    ### Determine that we are on linux
    osRegex = re.search('.*nux.?', sys.platform)
    # currentOS
    if (osRegex == None): # Windows
        osRegex = re.search('.*win.?', sys.platform)
        if (osRegex.group(0)):
            currentOS = tparams['params']['ostypes']['windowsType']
        else:
            # MAC, not defined
            currentOS = 0
            raise Exception('Undefined OS (Mac?) - code hasn\'t been tested.')
    else:
        currentOS = tparams['params']['ostypes']['linuxType']

    # Run the server's main loop
    myServer = displayServer(tparams)

    propertiesJSON = '''[{"property": "fullZoom", "enabled": "1"}, {"property": "hidePointer", "enabled": "1"}, {"property": "randomize", "enabled": "1"}, 
                    {"property": "delay", "enabled": "2.0"}, {"property": "autorotate", "enabled": "1"}, {"property": "showFilename", "enabled": "1"}, 
                    {"property": "noMenus", "enabled": "true"}, {"property": "quiet", "enabled": "1"}, {"property": "sort", "enabled": "0"}, {"property": "stretch", "enabled": "0"} ]'''


    criteriaJSON = '''[{"num":0,"criteriaType":"Year","booleanValue":"is","criteriaVal":"2018"},{"num":3,"criteriaType":"Year","booleanValue":"is","criteriaVal":"2013"},{"num":1,"criteriaType":"Date%20Range","booleanValue":"04/12/2016","criteriaVal":"04/21/2016"},{"num":2,"criteriaType":"Person","booleanValue":"is","criteriaVal":"Benjamin Lewis"},{"num":5,"criteriaType":"Person","booleanValue":"is","criteriaVal":"Jessica Lewis"},{"num":3,"criteriaType":"Month","booleanValue":"is","criteriaVal":"October"}]'''

    myServer.buildQuery(criteriaJSON)
    myServer.setSlideshowProperties(propertiesJSON)

    # myServer.run()
