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

        # self.commandString = "-FxZ -N -z -Y -D 2 --auto-rotate --action1 'echo \"%F\" >> " + os.path.join(rootDir, "misformedFiles.txt") + "'"
        self.commandArray = ["-FxZ", "-N", "-z", "-Y", "-D 2", "--auto-rotate", "--action1", "\'echo \"%F\" >> "  + os.path.join(rootDir, "misformedFiles.txt") +  "\'" ]
       
        self.masterQuery = ""
        self.xmlParams = xmlParams
        self.printDebug = False

        ### Connect to the database
        self.photoDatabase = sqlite3.connect(os.path.join(rootDir, "databases", self.xmlParams['params']['photoDatabase']['fileName']) )
        self.photoDatabase.text_factory = str  # For UTF-8 compatibility

        self.fileListName = '.slideshowFileList.txt'
        if (os.path.isfile(self.fileListName) ):
            os.remove(self.fileListName)

        self.p = None

        self.showRunning = False
        self.showRunningName = None

        self.stream = open(rootDir + '/serverLog.txt', 'w') 
        print >>self.stream, "Server log file opened."

        self.queryMachine = queryMaker.QueryMaker(self.xmlParams)
        self.screenManager = screen_manager.tvStateManager()

    ###### Slideshow function, avaliable as server call
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

    def startSlideshow(self, runLengthSec=3600):

        returnDict = {}
        errs = []
        debug = []
        
        print >>self.stream, 'Starting slideshow'

        self.screenManager.askForTvOn(runLengthSec)
        
        if currentOS != self.xmlParams['params']['ostypes']['linuxType']:
            errs.append('The current OS is not supported as a slideshow type.')
            returnDict['exceptions'] = errs;
            returnDict['debug'] = debug;
            return returnDict;

        self.p = subprocess.Popen(["/usr/local/bin/feh"] + self.commandArray + ["-f", self.fileListName])

        print >>self.stream, self.p

        self.showRunning = True
        returnDict['exceptions'] = errs;
        returnDict['debug'] = debug;
        threading.Timer(runLengthSec, self.endSlideshow).start()
        print >>self.stream, "The slideshow has launched"
        return returnDict;

    def endSlideshow(self):
        print "Ending slideshow"
        debug = []
        if self.p != None: 
            self.p.terminate()
        debug.append("Ending slideshow")
       
        returnDict = {}
        returnDict['exceptions'] = []
        returnDict['debug'] = debug
        self.showRunning = False
        self.showRunningName = None
        print "Show has now stopped, showServer"
        return json.dumps(returnDict)

    def buildQuery(self, criteriaJSON, **optionalParams):
        print >>self.stream, criteriaJSON

        if not ('loadingSavedShow' in optionalParams):
            self.showRunningName = None
            print "Loading arbitrary show"
        else:
            print "Loading a saved show"
        print self.showRunningName

        returnDict = {};
        errs = [];
        debug = [];

        debug.append("Root directory was: " + rootDir);
        print >>self.stream, "Building a query... {}".format(criteriaJSON)

        ## feh, the display program, locks the file in self.fileListName.
        ## Therefore, it is necessary to kill the subprocess that is running
        ## feh, if there is one, before overwriting the file.

        if self.p != None: 
            self.p.terminate()
            self.p.wait()
            
        print "Done killing the previous show"

        ## IMPORTANT NOTE: When building a query that will be INTERSECTED with something else but has UNIONS in it,
        ## it must be wrapped in '''SELECT * FROM ( <the query> ).
        ## Assume that we're only passing vetted JSON to the server here. 
        debug.append('JSON criteria was: ' + criteriaJSON);
        slideshowParams = json.loads(str(criteriaJSON))

        self.masterQuery = self.queryMachine.buildQueryFromJSON(criteriaJSON)

        if self.masterQuery != "":
            c = self.photoDatabase.cursor()
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
                rDict = self.startSlideshow()
                errs += rDict['exceptions']
                debug += rDict['debug']
            except:
                print "Error!" 
        else:
            errs.append('Invalid request.')

        assert False, "Nothing is starting the show running after determining a filename."
            
        debug.append("Final query was: " + self.masterQuery)
        print "Show running name is " + self.showRunningName

        returnDict['exceptions'] = errs;
        returnDict['debug'] = debug;
        return json.dumps(returnDict);

    def loadSavedShow(self, requestedShow):

        self.showRunningName = requestedShow

        runLength = 3600
        self.screenManager.askForTvOn(3600)

        # Obtain all of the parameters for the database where the website defines slideshows.
        siteDatabasePath = os.path.join(rootDir, 'site', self.xmlParams['params']['websiteParams']['siteDBname'])
        dbSchemaParams = self.xmlParams['params']['websiteParams']['siteDBschema']

        showDefTableName = dbSchemaParams['slideshowDefTable']['name']
        showNameCol = dbSchemaParams['slideshowDefTable']['showNameCol']
        showJsonCol = dbSchemaParams['slideshowDefTable']['jsonCol']

        getShowNamesQuery = '''SELECT {} FROM {}'''.format(showNameCol, showDefTableName)

        conn = sqlite3.connect(siteDatabasePath)

        c = conn.cursor()
        c.execute(getShowNamesQuery)
        fileResults = c.fetchall()
        # Convert the results to a list
        fileResults = [i[0] for i in fileResults]

        requestInListOfShows = (unicode(requestedShow) in set(fileResults))

        print "Here"
        print >>self.stream, fileResults

        if requestInListOfShows:
            # Get the corresponding JSON:
            getShowJSON = '''SELECT {} FROM {} WHERE {} = "{}"'''.format(showJsonCol, showDefTableName, showNameCol, unicode(requestedShow))
            c.execute(getShowJSON)
            jsonResult = c.fetchall()[0][0]
        else:
            # assert 1 == 0, "Need to implement a 'get all' function."
            jsonResult = '[{"num":0, "criteriaType":"All","booleanValue":"is", "criteriaVal":"all"}]'

        report = self.buildQuery(jsonResult, loadingSavedShow=True)
        return report

    def getShowRunningState(self):
        print 'Getting show running state'
        print "running name in server: " +  str(self.showRunningName)
        return json.dumps([self.showRunning, self.showRunningName])

    def run(self):
        self.server.register_function(self.startSlideshow, 'startSlideshow')
        self.server.register_function(self.setSlideshowProperties, 'setSlideshowProperties')
        self.server.register_function(self.buildQuery, 'buildQuery')
        self.server.register_function(self.loadSavedShow, 'loadSavedShow')
        self.server.register_function(self.endSlideshow, 'endSlideshow')
        self.server.register_function(self.getShowRunningState, 'getShowRunningState')
        self.server.serve_forever()


if __name__ == '__main__':
    ### Load the parameters from files

    with open(rootDir + '/config/params.xml') as stream:
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


    criteriaJSON = '''[{"criteriaType":"Year","booleanValue":"is","criteriaVal":2001}]'''
    criteriaJSON = '''[{"criteriaType":"Month","booleanValue":"is","criteriaVal":"3"}]'''
    criteriaJSON = '''[{"criteriaType":"Date Range","booleanValue":"2016/05/01","criteriaVal":"None"}]'''

    # myServer.buildQuery(criteriaJSON)
    # myServer.setSlideshowProperties(propertiesJSON)

    scheduleObj = showScheduler()
    myServer.run()
