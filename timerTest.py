#! /usr/bin/env python

import threading
import sqlite3
import datetime
import re
import xmltodict
import os
import json
import calendar

# showSchedule = [[2143, 2157, 'asdf'], [1250, 1300, 'fdsa']]
# print showSchedule

class scheduler():

    def __init__(self):
        self.showRunning = False;

        self.rootDir = os.path.abspath(os.path.dirname( __file__ ))
        with open(self.rootDir + '/config/params.xml') as stream:
            try:
                self.tparams = xmltodict.parse(stream.read())
            except Exception as exc:
                print(exc)
                exit(1)

        self.checkedDatabase = False
        self.lastSavedShows = ''
        self.checkForSchedules()
        # self.repeat()

    def checkForSchedules(self):

        webDatabase = self.tparams['params']['websiteParams']['siteDBname']
        print webDatabase
        dbPath = os.path.join(self.rootDir, 'site', webDatabase)
        conn = sqlite3.connect(dbPath)
        conn.text_factory = str  # For UTF-8 compatibility

        scheduleTable = self.tparams['params']['websiteParams']['siteDBschema']['scheduleTable']
        schTableName = scheduleTable['name']
        showNameCol = scheduleTable['paramNameCol']
        jsonCol = scheduleTable['jsonCol']
        scheduleParamName = scheduleTable['scheduleParamName']
        scheduleQuery = '''SELECT {} FROM {} WHERE {} = "{}"'''.format(jsonCol, schTableName, showNameCol, scheduleParamName)
        print scheduleQuery

        c = conn.cursor()
        c.execute(scheduleQuery)
        result = c.fetchall()
        self.allSavedShows =  json.loads(result[0][0])
        print self.allSavedShows

        if self.lastSavedShows != self.allSavedShows:
            print 'not equa'
            self.showSchedule = []
            for i in range(len(self.allSavedShows)):
                print str(i) + " " +  str(self.allSavedShows[i])
                currentShow = self.allSavedShows[i]
                showName = currentShow['showName']
                dow = currentShow['dayOfWeek']
                startTime = currentShow['startTime']
                stopTime = currentShow['stopTime']

                if dow = 'Every Day':
                    dowNum = 0
                else:
                    pass



        # if not self.checkedDatabase:
        #     self.lastSavedShows = self.allSavedShows


        self.checkedDatabase = True



    def repeat(self):
        print self.showRunning;
        currentTime = datetime.datetime.now().timetuple()
        hhmm = '{}{}'.format(currentTime[3], currentTime[4])

        if not self.showRunning:
            # Determine whether a show should be running. Takes the first
            # defined show. 

            for schedule in showSchedule:
                startTime = schedule[0]
                endTime = schedule[1]
                if (hhmm >= str(startTime) and hhmm < str(endTime)):
                    print "show ongoing"
                    self.schedule = schedule
                    self.showRunning = True
                    break

        else:
            # Show is running; see if it should stop
            startTime = self.schedule[0]
            endTime = self.schedule[1]
            if (hhmm >= str(endTime)):
                print "Show stopping!"
                self.showRunning = False
                self.schedule = []


        threading.Timer(5.0, self.repeat).start()

aa = scheduler()