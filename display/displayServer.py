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
import shlex
import thread
import threading
from scheduleRunner import showScheduler
from buildQuery import buildQueryFromJSON

import queryMaker
import screenPowerClient 

#### Get our root path
rootDir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

######### Set up the actual server #####################################

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/',)

class displayServer():

    def __init__(self, xmlParamFile):

        with open(xmlParamFile) as stream:
            try:
                self.xmlParams = xmltodict.parse(stream.read())
            except Exception as exc:
                print(exc)
                exit(1)
    
        ### Determine that we are on linux
        osRegex = re.search('.*nux.?', sys.platform)
        # currentOS
        if (osRegex == None): # Windows
            osRegex = re.search('.*win.?', sys.platform)
            if (osRegex.group(0)):
                self.currentOS = self.xmlParams['params']['ostypes']['windowsType']
            else:
                # MAC, not defined
                self.currentOS = 0
                raise Exception('Undefined OS (Mac?) - code hasn\'t been tested.')
        else:
            self.currentOS = self.xmlParams['params']['ostypes']['linuxType']


        self.server = SimpleXMLRPCServer(("127.0.0.1", int(self.xmlParams['params']['serverParams']['displayServerPort'])),
                                    requestHandler=RequestHandler)
        self.server.register_introspection_functions()

        self.screenManager = screenPowerClient.screenClient()
        self.queryMachine = queryMaker.QueryMaker(self.xmlParams)
        ### Connect to the database
        self.photoDatabase = sqlite3.connect(os.path.join(rootDir, "databases", self.xmlParams['params']['photoDatabase']['fileName']) )
        self.photoDatabase.text_factory = str  # For UTF-8 compatibility
        self.savedShowDatabase = sqlite3.connect(os.path.join(rootDir, "site", self.xmlParams['params']['websiteParams']['siteDBname']) )
        self.savedShowDatabase.text_factory = str  # For UTF-8 compatibility

        self.fileListName = '.slideshowFileList.txt'
        if (os.path.isfile(self.fileListName) ):
            os.remove(self.fileListName)

        self.display_executable = None

        self.showRunning = False
        self.showRunningName = None

        self.stream = open(rootDir + '/serverLog.txt', 'w') 
        print >>self.stream, "Server log file opened."

        self.printDebug = False
        # self.commandString = "-FxZ -N -z -Y -D 2 --auto-rotate --action1 'echo \"%F\" >> " + os.path.join(rootDir, "misformedFiles.txt") + "'"
        self.commandArray = ["-FxZ", "-N", "-z", "-Y", "-D 2", "--auto-rotate", "--action1", "\'echo \"%F\" >> "  + os.path.join(rootDir, "misformedFiles.txt") +  "\'" ]

    def startNamedSlideshow(self, requestedShow, runLength=3600):

        self.showRunningName = requestedShow

        self.screenManager.askForTvOn(runLength)

        # Obtain all of the parameters for the database where the website defines slideshows.
        dbSchemaParams = self.xmlParams['params']['websiteParams']['siteDBschema']

        showDefTableName = dbSchemaParams['slideshowDefTable']['name']
        showNameCol = dbSchemaParams['slideshowDefTable']['showNameCol']
        showJsonCol = dbSchemaParams['slideshowDefTable']['jsonCol']

        getShowNamesQuery = '''SELECT {} FROM {}'''.format(showNameCol, showDefTableName)

        c = self.savedShowDatabase.cursor()
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

        sql_query = self.queryMachine.buildQueryFromJSON(jsonResult)
        self.__startShow__(sql_query, runLength)

    def startSlideshowWithQuery(self, queryJSON, runLength=3600):
        self.showRunningName = "Custom"
        # print "query json in server: {}".format(queryJSON)
        
        sql_query = self.queryMachine.buildQueryFromJSON(queryJSON)
        print "Sql query is : {}".format(sql_query)

        self.__startShow__(sql_query, runLength)

    def __startShow__(self, SQL_query, runLength):

        returnDict = {};
        errs = [];
        debug = [];

        if self.display_executable != None: 
            self.display_executable.terminate()
            self.display_executable.wait()

        if SQL_query != "":
            c = self.photoDatabase.cursor()
            c.execute(SQL_query)
            fileResults = c.fetchall()

            rootTable =  self.xmlParams['params']['photoDatabase']['tables']['rootTable']
            rtName    =  rootTable['Name']
            rtKey     =  rootTable['Columns']['rootKey']
            
            if self.currentOS == self.xmlParams['params']['ostypes']['linuxType']:
                rtPath = rootTable['Columns']['linuxRootPath']
            else:
                rtPath = rootTable['Columns']['windowsRootPath']
                
            if self.currentOS != self.xmlParams['params']['ostypes']['linuxType']:
                errs.append('The current OS is not supported as a slideshow type.')
                returnDict['exceptions'] = errs;
                returnDict['debug'] = debug;
                return returnDict;

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

            f = open('fileListDebug.out', 'w')
            debug.append(str(len(fileResults)) + " files returned.")
            print "Found {} Files".format(len(fileResults))
            with open(str(self.fileListName), 'w') as file:
                for i in range(len(fileResults)):
                    photo_file = fileResults[i][1]
                    photo_root_key = fileResults[i][2]
                    photo_taken_date = fileResults[i][3]
                    print >>file, os.path.join(rootDict[photo_root_key], photo_file)

                    print >>f, '{0: <90}'.format( rootDict[photo_root_key] + photo_file)  +  '{0:>15}'.format(photo_taken_date)

            f.close()

            try:
            ###     rDict = self.startSlideshow()
                print >>self.stream, 'Starting slideshow'

                self.screenManager.askForTvOn(runLength)
                debug.append("Asking for television to turn on for the next {} seconds".format(runLength))
                
                print >>self.stream, "Done turning on TV, starting slideshow"
                 
                self.p = subprocess.Popen(["/usr/local/bin/feh"] + self.commandArray + ["-f", self.fileListName])

                debug.append("Slideshow is launching...")

                print >>self.stream, debug
                self.showRunning = True
                print >>self.stream, "The slideshow has launched"

            except:
                print "Error!" 
        else:
            errs.append('Invalid request.')

        returnDict['exceptions'] = errs;
        returnDict['debug'] = debug;

        # Set the slideshow to end in runLength seconds
        threading.Timer(runLength, self.endSlideshow).start()

        return json.dumps(returnDict);

    def endSlideshow(self):
        pass

    def setSlideshowProperties(self, propertiesJSON):

        returnDict = {};
        errs = [];
        debug = [];

        # # Set properties, according to page https://linux.die.net/man/1/feh
        # Action   |  -A
        # # Set to zoom fully with no borders: 
        # Auto-Zoom    |   -Z
        # Borderless window  | -x
        # Fullscreen  | -F
        # Hide pointer  | -Y
        # Randomize     | -z
        # Delay (sec)   | -D (int)
        # Auto-rotate based on image data | --auto-rotate 
        # Show filename  | -d
        # No menus   | -N

        debug.append("Args passed: " + str(propertiesJSON)  )
        properties = json.loads(propertiesJSON)

        #### As-yet unexplored properties:
        # Sort (with parameters) | -S <param> - name, filename, mtime, width, height, pixels, size, format. 
        # Stretch small images | -s

        self.commandArray = ["--action1", "\'echo \"%F\" >> "  + os.path.join(rootDir, "misformedFiles.txt") +  "\'" ]
        self.commandArray.append('--auto-rotate')

        # self.commandArray = ["-FxZ", "-N", "-z", "-Y", "-D 2", "--auto-rotate", "--action1", "\'echo \"%F\" >> "  + os.path.join(rootDir, "misformedFiles.txt") +  "\'" ]

        if properties['Fullscreen']:
            self.commandArray.append('-ZxF')

        if properties['Randomize']:
            self.commandArray.append('-z')

        if properties['Hide']:
            self.commandArray.append('-qNY')

        if "Delay" in properties:
            dly = properties["Delay"]
            if dly <= 0:
                dly = 1.0
            try:
                dly = float(dly)
            except ValueError:
                dly = 1.0
            argVal = "-D " + str(dly)
            self.commandArray.append(argVal)
        else:
            self.commandArray.append("-D 1")

        debug.append("Command array: " + str(self.commandArray) )

        if properties["Relaunch"]:
            rDict = self.startSlideshow();
            errs += rDict['exceptions']
            debug += rDict['debug']

        returnDict['exceptions'] = errs
        returnDict['debug'] = debug

        retVal = json.dumps(returnDict)
        print retVal
        return retVal

    def run(self):
        self.server.register_function(self.startSlideshowWithQuery, 'startSlideshowWithQuery')
        self.server.register_function(self.setSlideshowProperties, 'setSlideshowProperties')
        self.server.register_function(self.setSlideshowProperties, 'setSlideshowProperties')
        # self.server.register_function(self.buildQueryFromJSON, 'buildQueryFromJSON')
        self.server.register_function(self.startNamedSlideshow, 'startNamedSlideshow')
        self.server.register_function(self.endSlideshow, 'endSlideshow')
       # self.server.register_function(self.getShowRunningState, 'getShowRunningState')
        print "Running"
        self.server.serve_forever()
        
        
if __name__ == '__main__':
    ### Load the parameters from files
    configParamFile = os.path.join(rootDir, 'config', 'params.xml') 



    # Run the server's main loop
    myServer = displayServer(configParamFile)

    propertiesJSON = '''[{"property": "fullZoom", "enabled": "1"}, {"property": "hidePointer", "enabled": "1"}, {"property": "randomize", "enabled": "1"}, 
                    {"property": "delay", "enabled": "2.0"}, {"property": "autorotate", "enabled": "1"}, {"property": "showFilename", "enabled": "1"}, 
                    {"property": "noMenus", "enabled": "true"}, {"property": "quiet", "enabled": "1"}, {"property": "sort", "enabled": "0"}, {"property": "stretch", "enabled": "0"} ]'''


    criteriaJSON = '''[{"criteriaType":"Year","booleanValue":"is","criteriaVal":2001}]'''
    criteriaJSON = '''[{"criteriaType":"Month","booleanValue":"is","criteriaVal":"3"}]'''
    criteriaJSON = '''[{"criteriaType":"Date Range","booleanValue":"2016/05/01","criteriaVal":"None"}]'''

    # myServer.buildQuery(criteriaJSON)
    # myServer.setSlideshowProperties(propertiesJSON)

#    scheduleObj = showScheduler()
    myServer.run()
        