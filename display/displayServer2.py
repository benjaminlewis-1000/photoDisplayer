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
import screen_manager

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

        self.server = SimpleXMLRPCServer(("127.0.0.1", int(self.xmlParams['params']['serverParams']['displayServerPort'])),
                                    requestHandler=RequestHandler)
        self.server.register_introspection_functions()

        self.screenManager = screen_manager.tvStateManager()
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

        slideshowParams = json.loads(str(queryJSON))

        sql_query = self.queryMachine.buildQueryFromJSON(slideshowParams)

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

            # if currentOS == self.xmlParams['params']['ostypes']['linuxType']:
            #     rtPath = rootTable['Columns']['linuxRootPath']
            # else:
            #     rtPath = rootTable['Columns']['windowsRootPath']

            if currentOS != self.xmlParams['params']['ostypes']['linuxType']:
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
        pass

    def run(self):
        self.server.register_function(self.startSlideshow, 'startSlideshow')
        self.server.register_function(self.setSlideshowProperties, 'setSlideshowProperties')
        self.server.register_function(self.buildQuery, 'buildQuery')
        self.server.register_function(self.loadSavedShow, 'loadSavedShow')
        self.server.register_function(self.endSlideshow, 'endSlideshow')
        self.server.register_function(self.getShowRunningState, 'getShowRunningState')
        self.server.serve_forever()