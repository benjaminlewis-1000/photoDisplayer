 #! /usr/bin/env python

import os
import sqlite3
import xmltodict
import vars

project_path = os.path.abspath(os.path.join(__file__,"../.."))
script_path  = os.path.abspath(os.path.join(__file__,".."))

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
if vars.osType == vars.linuxType:
    rootPathFieldName = params['params']['photoDatabase']['tables']['rootTable']['Columns']['linuxRootPath']
    otherRootType = params['params']['photoDatabase']['tables']['rootTable']['Columns']['windowsRootPath']
elif vars.osType == vars.winType:
    rootPathFieldName = params['params']['photoDatabase']['tables']['rootTable']['Columns']['windowsRootPath']
    otherRootType = params['params']['photoDatabase']['tables']['rootTable']['Columns']['linuxRootPath']
else:
    assert(vars.osType == vars.winType or vars.osType == vars.linuxType)
    print "Not a windows or Linux system; this code hasn't been tested on a mac. More work required."

def checkPhotos(conn, params):

    rootKeyField = params['params']['photoDatabase']['tables']['rootTable']['Columns']['rootKey']
    rootTable = params['params']['photoDatabase']['tables']['rootTable']['Name']

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

    picsQuery = '''SELECT {}, {} FROM {}'''.format(rootDirCol, photoFileCol, photoTableName)
    c.execute(picsQuery)
    row = c.fetchone()
    count = 0
    while row != None:
        if count % 1000 == 0:
            print "Done {} files".format(count)
        rootDir = rootDict[row[0]]
        filename = row[1]
        fullpath = os.path.join(rootDir, filename)
        if not os.path.isfile(fullpath):
            print os.path.join(rootDir, filename) + " is not a file"
        row = c.fetchone()
        count += 1

checkPhotos(conn, params)   