#! /usr/bin/env python

import os
import datetime
import time
import xmltodict
import sqlite3
from getExif import getExifData
import json
import vars

def addPhoto(basePath, fileRelPath, currentRootDirNum, params, conn, nameDict):
    conn.row_factory = sqlite3.Row

    fullPath = os.path.join(basePath, fileRelPath)

    if not fileRelPath.endswith(tuple([".JPG", ".jpg", ".jpeg", ".JPEG"])):
        return

    c = conn.cursor()

    # Find the time that the photo was modified at, according to its filesystem data.
    last_modified_date = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(fullPath)))

    photoTableName = params['params']['photoDatabase']['tables']['photoTable']['Name']
    photoCols = params['params']['photoDatabase']['tables']['photoTable']['Columns']
    photoFileCol = photoCols['photoFile']
    modDateCol = photoCols['modifyDate']
    rootDirCol = photoCols['rootDirNum']
    photoKeyCol = photoCols['photoKey']

    # Determin whether the photo is in the database already.
    photoInTableQuery = '''SELECT {}, {}, {}, {} FROM {} WHERE {} = ? AND {} = ?'''.format(photoFileCol, modDateCol, rootDirCol, photoKeyCol, photoTableName, photoFileCol, rootDirCol)

    c.execute(photoInTableQuery, (fileRelPath, currentRootDirNum))

    row = c.fetchone()

    # Determine whether we have already entered this photo in the table and it's up to date.
    if row != None:
        recordedModDate = row[1]
        if recordedModDate >= last_modified_date:
            # Do nothing - already recorded and up to date.
            return

    exifData = getExifData(fullPath, True)
    if exifData == -1:
        # Something in the photo data lookup failed, so we are going 
        # to skip this for now and come back on a future update.
        return

    try:
        photoData = json.loads(exifData)
    except Exception as e:
        print "File: " + fullPath
        print exifData
        print "Error in photoHandler! : " + str(e)
        return

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
        # This is the case where we already have the data in the database, but 
        # the photo has been updated since then. 
        # print '{}, {}, {}' % (str(row[0]), str(row[1]), str(row[2]))
        # Update the photo
        recordedModDate = row[1]
        rootDirNum = row[2]
        photoID = row[3]
        if recordedModDate < last_modified_date:
            pass 
            # Need to do an update
            print 'Need to update ' + fullPath
            clearPhotoLinks(conn, photoID, params)

            updatePhotoQuery = '''UPDATE {} SET {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ?, {} = ? WHERE {} = ? AND {} = ?'''.format(photoTableName, \
                photoDateColumn, modDateCol, photoYearColumn, photoMonthColumn, photoDayColumn, photoHourColumn, photoMinuteColumn, photoTimezoneColumn, insertDateColumn, houseNumColumn, streetColumn, cityColumn, stateColumn, postcodeCoulumn, countryColumn, latColumn, longColumn, \
                photoFileCol, rootDirNumColumn)

            try:
                c.execute(updatePhotoQuery, (phDate, last_modified_date, phYear, phMonth, phDay, phHour, phMin, phTZ, phInsertDate, phHouseNum, phRoad, phCity, phState, phPost, phCountry, phLat, phLon, fileRelPath, currentRootDirNum))
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
    # Remove the links in linker tables to the photo's unique ID, so that we can then delete or update
    # the photo's record in the photo table.
    # Tags removed include people and tags from user, Google, and Clarifai
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    linkerTable = params['params']['photoDatabase']['tables']['photoLinkerTable']['Name']
    linkerPhoto = params['params']['photoDatabase']['tables']['photoLinkerTable']['Columns']['linkerPhoto']

    userTagTable = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['Name']
    clarifaiTagTable = params['params']['photoDatabase']['tables']['commentLinkerClarifaiTable']['Name']
    googTagTable = params['params']['photoDatabase']['tables']['commentLinkerGoogleTable']['Name']

    userTagPhoto = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['Columns']['commentLinkerPhoto']
    clarifaiTagPhoto = params['params']['photoDatabase']['tables']['commentLinkerClarifaiTable']['Columns']['commentLinkerPhoto']
    googTagPhoto = params['params']['photoDatabase']['tables']['commentLinkerGoogleTable']['Columns']['commentLinkerPhoto']

    deletePeople = '''DELETE FROM {} WHERE {} = ?'''.format(linkerTable, linkerPhoto)
    c.execute(deletePeople, (photoKeyID,))

    delTagsUser = '''DELETE FROM {} WHERE {} = ?'''.format(userTagTable, userTagPhoto)
    c.execute(delTagsUser, (photoKeyID,))

    delTagsClarifai = '''DELETE FROM {} WHERE {} = ?'''.format(clarifaiTagTable, clarifaiTagPhoto)
    c.execute(delTagsClarifai, (photoKeyID,))

    delTagsGoogle = '''DELETE FROM {} WHERE {} = ?'''.format(googTagTable, googTagPhoto)
    c.execute(delTagsGoogle, (photoKeyID,))

    # Commit to database at the end to make change permanent
    conn.commit()

def checkPhotosAtEnd(conn, params):

    # Perform a check at the end that all photos in the database are still on disk. If a photo is not
    # on disk (i.e. has been deleted) then it should be removed from the database. 

    # IMPORTANT! Set the row factory for the database. 
    conn.row_factory = sqlite3.Row

    rootKeyField = params['params']['photoDatabase']['tables']['rootTable']['Columns']['rootKey']
    rootTable = params['params']['photoDatabase']['tables']['rootTable']['Name']

    excludedDirectories = params['params']['excludeDirs']['dir']

    if vars.osType == vars.linuxType:
        rootPathFieldName = params['params']['photoDatabase']['tables']['rootTable']['Columns']['linuxRootPath']
        otherRootType = params['params']['photoDatabase']['tables']['rootTable']['Columns']['windowsRootPath']
    elif vars.osType == vars.winType:
        rootPathFieldName = params['params']['photoDatabase']['tables']['rootTable']['Columns']['windowsRootPath']
        otherRootType = params['params']['photoDatabase']['tables']['rootTable']['Columns']['linuxRootPath']
    else:
        assert(vars.osType == vars.winType or vars.osType == vars.linuxType)
        print "Not a windows or Linux system; this code hasn't been tested on a mac. More work required."

    rootQuery = '''SELECT {}, {} FROM {}'''.format(rootPathFieldName, rootKeyField, rootTable)
    c = conn.cursor()
    c.execute(rootQuery)

    row = c.fetchone()
    rootDict = {}
    while row != None:
        key = row[1]
        dir = row[0]
        rootDict[key] = dir
        row = c.fetchone()

    photoTableName = params['params']['photoDatabase']['tables']['photoTable']['Name']
    photoCols = params['params']['photoDatabase']['tables']['photoTable']['Columns']
    photoFileCol = photoCols['photoFile']
    rootDirCol = photoCols['rootDirNum']
    photoKeyCol = photoCols['photoKey']

    picsQuery = '''SELECT {}, {}, {} FROM {}'''.format(rootDirCol, photoFileCol, photoKeyCol, photoTableName)
    c.execute(picsQuery)
    row = c.fetchone()
    count = 0
    while row != None:
        if count % 1000 == 0:
            print "Done {} files".format(count)
        rootDir = rootDict[row[0]]
        filename = row[1]
        photoKeyID = row[2]
        fullpath = os.path.join(rootDir, filename)
        markForDeletion = False
        if not os.path.isfile(fullpath):
            print os.path.join(rootDir, filename) + " is not a file"
            markForDeletion = True

        for exDir in excludedDirectories:
            if fullpath.startswith(exDir):
                print "Bad start file: {} in {}".format(filename, exDir)
                markForDeletion = True

        if markForDeletion:
            print "Deleting!"
            clearPhotoLinks(conn, photoKeyID, params)
            delPhotoQuery = '''DELETE FROM {} WHERE {} = ? AND {} = ?'''.format(photoTableName, photoFileCol, rootDirCol)
            print delPhotoQuery + " " + filename
            d = conn.cursor()
            d.execute(delPhotoQuery, (filename, rootDir))
            conn.commit()

        row = c.fetchone()
        count += 1

def insertName(name, conn, photoKeyID, params, nameDict):

    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Use a nameDict to speed up database lookups - if we have seen that person's name before,
    # we get their unique ID number from the database and put it in the nameDict such that
    # nameDict[person] = uuid. 

    # Python passed nameDict by reference, so updating it here updates it in the calling function.
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
        ## Check if the person exists in the database already
        personExistsQuery = '''SELECT {} FROM {} WHERE {} = ?'''.format(personKeyCol, personTableName, personNameCol)

        c.execute(personExistsQuery, (utf_name,))

        row = c.fetchone()

        if row != None:
            # Person is in the database
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

    # Insert a record in the linker table, with photo_uuid tied to person_uuid.
    insertLinkInTable = '''INSERT INTO {} ({}, {}) VALUES (?, ?)'''.format(linkerTable, linkerPhoto, linkerPerson)
    c.execute(insertLinkInTable, (photoKeyID, nameDict[name]))
    # Commit to database so that the value persists in the DB even if the program is killed. 
    conn.commit()

def linkTags(conn, photoKeyID, userTags, clarifaiTags, googTags, params):

    conn.row_factory = sqlite3.Row
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
