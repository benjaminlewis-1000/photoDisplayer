#! /usr/bin/env python

import os
import datetime
import time
import xmltodict
import sqlite3
from getExif import getExifData
import json

def addPhoto(basePath, fileRelPath, currentRootDirNum, params, conn, nameDict):

    fullPath = os.path.join(basePath, fileRelPath)


    if not fileRelPath.endswith(tuple([".JPG", ".jpg", ".jpeg", ".JPEG"])):
        return

    c = conn.cursor()

    last_modified_date = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(fullPath)))

    # print fullPath + "  " + str(last_modified_date)

    photoTableName = params['params']['photoDatabase']['tables']['photoTable']['Name']
    photoCols = params['params']['photoDatabase']['tables']['photoTable']['Columns']
    photoFileCol = photoCols['photoFile']
    modDateCol = photoCols['modifyDate']
    rootDirCol = photoCols['rootDirNum']
    photoKeyCol = photoCols['photoKey']

    photoInTableQuery = '''SELECT {}, {}, {}, {} FROM {} WHERE {} = ? AND {} = ?'''.format(photoFileCol, modDateCol, rootDirCol, photoKeyCol, photoTableName, photoFileCol, rootDirCol)

    c.execute(photoInTableQuery, (fileRelPath, currentRootDirNum))

    row = c.fetchone()

    photoData = json.loads(getExifData(fullPath, False))

    photoDateColumn  = photoCols['photoDate']
    rootDirNumColumn  = photoCols['rootDirNum']
    photoYearColumn  = photoCols['photoYear']
    photoMonthColumn  = photoCols['photoMonth']
    photoDayColumn  = photoCols['photoDay']
    photoHourColumn  = photoCols['photoHour']
    photoMinuteColumn  = photoCols['photoMinute']
    photoTimezoneColumn  = photoCols['photoGMT']
    insertDateColumn  = photoCols['insertDate']
    houseNumColumn  = photoCols['houseNum']
    streetColumn  = photoCols['street']
    cityColumn  = photoCols['city']
    stateColumn  = photoCols['state']
    postcodeCoulumn  = photoCols['postcode']
    countryColumn  = photoCols['country']
    latColumn  = photoCols['lat']
    longColumn  = photoCols['long']

    # photoFile = relPath
    phDate = photoData['ISO8601']
    # modDate = last_modified_date
    # rootDirNum = currentRootDirNum
    phYear = photoData['year']
    phMonth = photoData['month']
    phDay = photoData['day']
    phHour = photoData['hour']
    phMin = photoData['min']
    phSec = photoData['sec']
    phTZ = photoData['TimeZone']
    phInsertDate = time.strftime("%Y-%m-%d %H:%M:%S")
    phHouseNum = photoData['house_number']
    phRoad = photoData['road']
    phCity = photoData['city']
    phState = photoData['state']
    phPost = photoData['postcode']
    phCountry = photoData['country']
    phLat = photoData['latitude']
    phLon = photoData['longitude']

    if row != None:
        # print '{}, {}, {}' % (str(row[0]), str(row[1]), str(row[2]))
        # Update the photo
        recordedModDate = row[1]
        rootDirNum = row[2]
        photoID = row[3]
        if recordedModDate < last_modified_date:
            pass 
            # Need to do an update
            print 'Need to update' + fullPath + "  " + str(last_modified_date)
            getExifData(fullPath, False)
            clearPhotoLinks(conn, photoID, params)

            updatePhotoQuery = '''UPDATE {} SET {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ? WHERE {} = ? AND {} = ?'''.format(photoTableName, \
                photoDateColumn, modDateCol, photoYearColumn, photoMonthColumn, photoDayColumn, photoHourColumn, photoMinuteColumn, photoTimezoneColumn, insertDateColumn, houseNumColumn, streetColumn, cityColumn, stateColumn, postcodeCoulumn, countryColumn, latColumn, longColumn, \
                photoFileCol, rootDirNumColumn)

            try:
                c.execute(updatePhotoQuery, (phDate, last_modified_date, phYear, phMonth, phDay, phHour, phMin, phTZ, phInsertDate, phHouseNum, phRoad, phCity, phState, phPost, phCountry, phLat, phLon, \
                    fileRelPath, currentRootDirNum))
                conn.commit()

            except sqlite3.OperationalError as oe:
                print str(oe)
                exit(1)

            for name in photoData['names']:
                insertName(name, conn, photoID, params, nameDict)

            linkTags(conn, photoID, photoData['picasaTags'], photoData['autoTagsClarifai'], photoData['autoTagsGoogle'], params)
        else:
            pass
            # Do nothing 
    else:
        print "Empty..."
        print "Currently processing image: " + fullPath

        photoInsertQuery = '''INSERT INTO {} ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )'''.format(photoTableName, photoFileCol, photoDateColumn, modDateCol, rootDirNumColumn, photoYearColumn, photoMonthColumn, photoDayColumn, photoHourColumn, photoMinuteColumn, photoTimezoneColumn, insertDateColumn, houseNumColumn, streetColumn, cityColumn, stateColumn, postcodeCoulumn, countryColumn, latColumn, longColumn)

        try:
            c.execute(photoInsertQuery, (fileRelPath, phDate, last_modified_date, currentRootDirNum, phYear, phMonth, phDay, phHour, phMin, phTZ, phInsertDate, phHouseNum, phRoad, phCity, phState, phPost, phCountry, phLat, phLon))

            conn.commit()
        except sqlite3.OperationalError as oe:
            print str(oe)
            print "Error in SQL query!"
            exit(1)

        photoID = c.lastrowid

        for name in photoData['names']:
            insertName(name, conn, photoID, params, nameDict)

        linkTags(conn, photoID, photoData['picasaTags'], photoData['autoTagsClarifai'], photoData['autoTagsGoogle'], params)

def clearPhotoLinks(conn, photoKeyID, params):
    c = conn.cursor()

    linkerTable = params['params']['photoDatabase']['tables']['photoLinkerTable']['Name']
    linkerPhoto = params['params']['photoDatabase']['tables']['photoLinkerTable']['Columns']['linkerPhoto']

    deletePeople = '''DELETE FROM {} WHERE {} = ?'''.format(linkerTable, linkerPhoto)
    c.execute(deletePeople, (photoKeyID,))

    # deleteTags

    userTagTable = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['Name']
    clarifaiTagTable = params['params']['photoDatabase']['tables']['commentLinkerClarifaiTable']['Name']
    googTagTable = params['params']['photoDatabase']['tables']['commentLinkerGoogleTable']['Name']

    userTagPhoto = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['Columns']['commentLinkerPhoto']
    clarifaiTagPhoto = params['params']['photoDatabase']['tables']['commentLinkerClarifaiTable']['Columns']['commentLinkerPhoto']
    googTagPhoto = params['params']['photoDatabase']['tables']['commentLinkerGoogleTable']['Columns']['commentLinkerPhoto']

    delTagsUser = '''DELETE FROM {} WHERE {} = ?'''.format(userTagTable, userTagPhoto)
    c.execute(delTagsUser, (photoKeyID,))

    delTagsUser = '''DELETE FROM {} WHERE {} = ?'''.format(clarifaiTagTable, clarifaiTagPhoto)
    c.execute(delTagsUser, (photoKeyID,))

    delTagsUser = '''DELETE FROM {} WHERE {} = ?'''.format(googTagTable, googTagPhoto)
    c.execute(delTagsUser, (photoKeyID,))

    conn.commit()

def insertName(name, conn, photoKeyID, params, nameDict):
    c = conn.cursor()

    if name not in nameDict:

        photoTableName = params['params']['photoDatabase']['tables']['photoTable']['Name']
        photoCols = params['params']['photoDatabase']['tables']['photoTable']['Columns']
        photoKeyCol = photoCols['photoKey']

        personTableName = params['params']['photoDatabase']['tables']['peopleTable']['Name']
        personKeyCol = params['params']['photoDatabase']['tables']['peopleTable']['Columns']['peopleKey']
        personNameCol = params['params']['photoDatabase']['tables']['peopleTable']['Columns']['personName']

        # TODO: Name in UTF-8
        try:
            utf_name = name.encode('utf-8')
        except UnicodeDecodeError as ude:
            utf_name = name
            # utf_name = unicode(str(name), "utf-8", "ignore")
        # print utf_name
        ## Check if the person exists
        personExistsQuery = '''SELECT {} FROM {} WHERE {} = ?'''.format(personKeyCol, personTableName, personNameCol)

        c.execute(personExistsQuery, (utf_name,))

        row = c.fetchone()

        if row != None:
            personID = row[0]
            # Sanity check - make sure only one person has that name in the database
            numPeopleQuery = '''SELECT COUNT(*) FROM {} WHERE {} = ?'''.format(personTableName, personNameCol)
            c.execute(numPeopleQuery, (utf_name,))
            numRow = c.fetchone()
            assert numRow[0] == 1
            nameDict[name] = personID
            
        else:
            newPersonQuery = '''INSERT INTO {} ({}) VALUES (?)'''.format(personTableName, personNameCol)
            c.execute(newPersonQuery, (utf_name,))
            conn.commit()
            personID = c.lastrowid
            nameDict[name] = personID

    linkerTable = params['params']['photoDatabase']['tables']['photoLinkerTable']['Name']
    linkerPerson = params['params']['photoDatabase']['tables']['photoLinkerTable']['Columns']['linkerPeople']
    linkerPhoto = params['params']['photoDatabase']['tables']['photoLinkerTable']['Columns']['linkerPhoto']

    insertLinkInTable = '''INSERT INTO {} ({}, {}) VALUES (?, ?)'''.format(linkerTable, linkerPhoto, linkerPerson)
    c.execute(insertLinkInTable, (photoKeyID, nameDict[name]))
    conn.commit()

def linkTags(conn, photoKeyID, userTags, clarifaiTags, googTags, params):
    c = conn.cursor()

    userTagTable = params['params']['photoDatabase']['tables']['commentLinkerUserTable']
    clarifaiTagTable = params['params']['photoDatabase']['tables']['commentLinkerClarifaiTable']
    googTagTable = params['params']['photoDatabase']['tables']['commentLinkerGoogleTable']

    tables = (userTagTable, clarifaiTagTable, googTagTable)
    tags = (userTags, clarifaiTags, googTags)

    for i in range(len(tables)):
        tableName = tables[i]['Name']
        photoField = tables[i]['Columns']['commentLinkerPhoto']
        linkerTagField = tables[i]['Columns']['commentLinkerTag']
        tagProbField = tables[i]['Columns']['commentLinkerTagProbability']

        tagList = tags[i]

        for tagPair in tagList:
            tagText = tagPair[0]
            tagProb = tagPair[1]
            # print tagText
            # print tagPair

            tagQuery = '''INSERT INTO {} ({}, {}, {}) VALUES (?, ?, ?)'''.format(tableName, photoField, linkerTagField, tagProbField)

            c.execute(tagQuery, (photoKeyID, tagText, tagProb))

    conn.commit()

if __name__ == '__main__':

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

    subdir = "/home/lewis/Pictures"

    files = os.listdir(subdir)
    # print files

    personNameDict = {}

    for name in files:
        # relPath = os.path.join(subdir, name)
        addPhoto(subdir, name, 1, params, conn, personNameDict)
        # try:
        #     mtime = os.path.getmtime(relPath)
        # except OSError:
        #     mtime = 0
        # last_modified_date = datetime.fromtimestamp(mtime)