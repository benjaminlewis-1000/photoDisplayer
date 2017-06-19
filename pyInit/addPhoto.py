#! /usr/bin/env python

import os
import datetime
import time
import xmltodict
import sqlite3
from getExif import getExifData

subdir = "/home/lewis/Pictures"

files = os.listdir(subdir)
print files

def addPhoto(fullPath, currentRootDirNum, params, conn):
    print "Currently processing image: {} \n".format(fullPath)

    c = conn.cursor()

    last_modified_date = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(os.path.getmtime(fullPath)))

    print fullPath + "  " + str(last_modified_date)

    photoTableName = params['params']['photoDatabase']['tables']['photoTable']['Name']
    photoCols = params['params']['photoDatabase']['tables']['photoTable']['Columns']
    photoFileCol = photoCols['photoFile']
    modDateCol = photoCols['modifyDate']
    rootDirCol = photoCols['rootDirNum']

    photoInTableQuery = '''SELECT {}, {}, {} FROM {} WHERE {} = ? AND {} = ?'''.format(photoFileCol, modDateCol, rootDirCol, photoTableName, photoFileCol, rootDirCol)

    c.execute(photoInTableQuery, (fullPath, currentRootDirNum))

    row = c.fetchone()
    if row != None:
        print '{}, {}, {}' % (row[0], row[1], row[2])
        # Update the photo
        recordedModDate = row[1]
        rootDirNum = row[2]
        if recordedModDate < last_modified_date:
            pass 
            # Need to do an update
            getExifData(fullPath, False)
        else:
            pass
            # Do nothing 
    else:
        print "Empty..."
        print getExifData(fullPath, False)

        photoDateColumn  = photoCols['photoDate']
        rootDirNumColumn  = photoCols['rootDirNum']
        photoYearColumn  = photoCols['photoYear']
        photoMonthColumn  = photoCols['photoMonth']
        photoDayColumn  = photoCols['photoDay']
        photoHourColumn  = photoCols['photoHour']
        photoMinuteColumn  = photoCols['photoMinute']
        photoGMTColumn  = photoCols['photoGMT']
        insertDateColumn  = photoCols['insertDate']
        houseNumColumn  = photoCols['houseNum']
        streetColumn  = photoCols['street']
        cityColumn  = photoCols['city']
        stateColumn  = photoCols['state']
        postcodeCoulumn  = photoCols['postcode']
        countryColumn  = photoCols['country']
        latColumn  = photoCols['lat']
        longColumn  = photoCols['long']

        photoInsertQuery = '''INSERT INTO {} ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}) VALUES ("?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?" )'''.format(photoTableName, photoFileCol, photoDateColumn, modDateCol, rootDirNumColumn, photoYearColumn, photoMonthColumn, photoDayColumn, photoHourColumn, photoMinuteColumn, photoGMTColumn, insertDateColumn, houseNumColumn, streetColumn, cityColumn, stateColumn, postcodeCoulumn, countryColumn, latColumn, longColumn)

        print photoInsertQuery
    # VALUES ("$utf_filename", 
    #     "$data{'TakenDate'}", "$fileLastEditDate", 
    #     $rootDirNum, $data{'Year'}, 
    #     $data{'Month'}, $data{'Day'}, 
    #     $data{'Hour'}, $data{'Minute'}, 
    #     $data{'TimeZone'}, "$dbInsertionDate",
    #     "$data{'house_number'}", "$data{'road'}",
    #     "$data{'city'}", "$data{'state'}",
    #     "$data{'postcode'}", "$data{'country'}",
    #     "$data{'Latitude'}", "$data{'Longitude'}"
    # )/;



project_path = os.path.abspath(os.path.join(__file__,"../.."))
script_path  = os.path.abspath(os.path.join(__file__,".."))
## Open the params.xml file for the configuration parameters
with open(os.path.join(project_path, 'config/params.xml') ) as stream:
    try:
        params = xmltodict.parse(stream.read())
    except Exception as exc:
        print(exc)
        exit(1)

dbName = params['params']['photoDatabase']['fileName']


## Connect to the database. Also set up Ctrl-C Handling
conn = sqlite3.connect(os.path.join(project_path, 'databases', dbName))
conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")

for name in files:
    fullPath = os.path.join(subdir, name)
    addPhoto(fullPath, 1, params, conn)
    # try:
    #     mtime = os.path.getmtime(fullPath)
    # except OSError:
    #     mtime = 0
    # last_modified_date = datetime.fromtimestamp(mtime)