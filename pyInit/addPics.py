#! /usr/bin/env python

import os
import re
import sqlite3
import xmltodict
import argparse
from Tkinter import Tk
import tkMessageBox
from tkFileDialog import askdirectory
from time import sleep
import os
import subprocess
import psutil
import signal
import time

import photoHandler

import vars

project_path = os.path.abspath(os.path.join(__file__,"../.."))
script_path  = os.path.abspath(os.path.join(__file__,".."))


def isSubDir(compDir, possibleSubDir):
    # print compDir
    # print possibleSubDir
    try:
        cdir = compDir.encode('utf-8')
    except UnicodeDecodeError as ude:
        cdir = compDir

    try:
        pdir = possibleSubDir.encode('utf-8', errors='ignore')
    except UnicodeDecodeError as ude:
        pdir = possibleSubDir

    if re.search(r'' + cdir, pdir, re.UNICODE) is None:
        return False
    else:
        return True


def getRoots(conn, args, params):
    c = conn.cursor()
    if vars.osType == vars.linuxType:
        rootPathFieldName = params['params']['photoDatabase']['tables']['rootTable']['Columns']['linuxRootPath']
        otherRootType = params['params']['photoDatabase']['tables']['rootTable']['Columns']['windowsRootPath']
    elif vars.osType == vars.winType:
        rootPathFieldName = params['params']['photoDatabase']['tables']['rootTable']['Columns']['windowsRootPath']
        otherRootType = params['params']['photoDatabase']['tables']['rootTable']['Columns']['linuxRootPath']
    else:
        assert(vars.osType == vars.winType or vars.osType == vars.linuxType)
        print "Not a windows or Linux system; this code hasn't been tested on a mac. More work required."

    rootKeyField = params['params']['photoDatabase']['tables']['rootTable']['Columns']['rootKey']
    rootTable = params['params']['photoDatabase']['tables']['rootTable']['Name']

    assert rootKeyField != ""
    assert rootTable != ""

    fieldQuery = '''SELECT {}, {}, {} FROM {}'''.format(rootKeyField, rootPathFieldName, otherRootType, rootTable)

    try:
        c.execute(fieldQuery)
    except sqlite3.OperationalError as oe:
        print "\nOperational Error:    " + str(oe)
        print "Failing query:        " + str(fieldQuery)
        print "\nExiting\n\n"
        exit(1)

    rootDirRows = {}
    rootDirPathsList = []

    row = c.fetchone()
    while row is not None:
        keyVal = row[0]
        thisOSPath = row[1]
        otherOSPath = row[2]
        if thisOSPath == None:
            print "The path in " + vars.osType + " corresponding to the path " + otherOSPath + " in " + vars.otherOStype + " is undefined."


            window = Tk()
            window.option_add('*Dialog.msg.width', 75)
            window.withdraw() # we don't want a full GUI, so keep the root window from appearing

            acceptedVal = 'No'
            while acceptedVal != 'yes':
                newDirName = askdirectory() # show an "Open" dialog box and return the path to the selected file
                if newDirName == '':
                    window.option_add('*Dialog.msg.width', 20)
                    exitVal = tkMessageBox.askquestion("Confirmation", "Exit?", icon='warning')
                    if exitVal == 'yes':
                        exit(1)
                    window.option_add('*Dialog.msg.width', 75)
                else:
                    acceptedVal = tkMessageBox.askquestion("Exit", "{} directory: {}\n{} directory: {}".format(vars.osType, newDirName, vars.otherOStype, otherOSPath), icon='warning')
            
            print "TODO: Verify that the directories match in some way"


            thisOSPath = newDirName
            assert os.path.isdir(newDirName)
            insertQuery = '''UPDATE {} SET {} = ? WHERE {} = ? '''.format(rootTable, rootPathFieldName, otherRootType)

            tmpc = conn.cursor()
            try:
                tmpc.execute(insertQuery, (thisOSPath, otherOSPath ) )
                conn.commit()
            except Exception as e:
                print "Unknown exception: " + str(e)

        thisOSPath = re.sub(r'[\\/]$', '', thisOSPath)
        rootDirRows[thisOSPath] = keyVal

        row = c.fetchone()

    if args.addRoot:
        if args.addRoot == "":

            acceptedVal = 'No'
            while acceptedVal != 'yes':
                newDirName = askdirectory() # show an "Open" dialog box and return the path to the selected file
                if newDirName == '':
                    window.option_add('*Dialog.msg.width', 20)
                    exitVal = tkMessageBox.askquestion("Confirmation", "Exit?", icon='warning')
                    if exitVal == 'yes':
                        exit(1)
                    window.option_add('*Dialog.msg.width', 75)
                else:
                    acceptedVal = tkMessageBox.askquestion("Exit", vars.osType + " directory: "+ newDirName.encode('utf-8') , icon='warning')
        else:
            newDirName = args.addRoot

        isdir = os.path.isdir(newDirName)
        isabsdir = os.path.isabs(newDirName)

        if not os.path.isabs(newDirName):
            newDirName = os.path.expanduser(newDirName)
            newDirName = os.path.abspath(newDirName)

        print newDirName

        isNewDirValid = os.path.isdir(newDirName) # Should be true if it's a directory
        for root in list(rootDirRows.keys()):
            if isSubDir(root, newDirName):
                isNewDirValid = False

        if isNewDirValid:
            newRootQuery = '''INSERT INTO {} ({}) VALUES (?) '''.format(rootTable, rootPathFieldName)

            print "Inserting new dir : " + newDirName
            try:
                c.execute(newRootQuery, (unicode(str(newDirName), "utf-8", "ignore"),))
                conn.commit()
            except sqlite3.OperationalError as oe:
                print "Operational error: " + str(oe)
                print "Problem query:     " + str(newRootQuery)
                print "Exiting. \n"
                exit(1)

            # Get the root key of the new directory
            rootKey = c.lastrowid  # SQLite function 
            rootDirRows[newDirName] = rootKey

    return rootDirRows


def getUniqueSubDirs(rootsList):
    print "Obtaining all subdirectories of the roots and de-duplicating them..."
    subDirsDict = dict()
    for eachRoot in rootsList:
        currentSubDirs = []
        for root, dirs, files in os.walk(eachRoot):
            # print root
            root = re.sub(r'[\\/]$', '', root, re.UNICODE)
            currentSubDirs.append(root)
            # print dirs 
        subDirsDict[eachRoot] = currentSubDirs

    for currentRoot in rootsList:
        otherRoots = list(set(rootsList) - set([currentRoot]))
        currentSubDirs = subDirsDict[currentRoot]

        for other in otherRoots:
            otherSubDirs = subDirsDict[other]
            if isSubDir(other, currentRoot):
                pass
            else:
                if isSubDir(currentRoot, other):
                    # print set(currentSubDirs)
                    # print set(currentSubDirs).intersection(set(otherSubDirs))
                    # print set(otherSubDirs)
                    # print list(set(currentSubDirs) - set(currentSubDirs).intersection(set(otherSubDirs)) )
                    currentSubDirs = list(set(currentSubDirs) - set(currentSubDirs).intersection(set(otherSubDirs)) )

        subDirsDict[currentRoot] = currentSubDirs

    for currentRoot in rootsList:
        subdirs = subDirsDict[currentRoot]
        # print subdirs
        for i in range(len(subdirs)):
            subdirs[i] = re.sub(r''+ currentRoot, '', subdirs[i])
            subdirs[i] = re.sub(r'^[\\/]', '', subdirs[i])
        subDirsDict[currentRoot] = subdirs

    return subDirsDict


if __name__ == '__main__':

    print "TODO! Encode all input with '.encode('utf-8')'."
    # TODO: Expand a directory passed via command line
    # sleep(3)

    ## Open the params.xml file for the configuration parameters
    with open(os.path.join(project_path, 'config/params.xml') ) as stream:
        try:
            params = xmltodict.parse(stream.read())
        except Exception as exc:
            print(exc)
            exit(1)

    geoServerPort = params['params']['serverParams']['geoServerPort']

    # Kill the previously running server on this port, if applicable
    for process in psutil.process_iter():
        # print process.cmdline
        cmdline = process.cmdline
        if re.search(r'geoServer', str(cmdline) ) :
            print process.cmdline
            if str(geoServerPort) in cmdline:
                print "Killing previous version of geoServer..."
            process.terminate()
            break

    proc = subprocess.Popen(["python", os.path.join(script_path, "geoServer.py"), "8040"])
        # [] + self.commandArray + ["-f", self.fileListName])
        #sleep(5)
        #if not self.p.poll():

    parser = argparse.ArgumentParser(description='Python version of the photo display program.')
    parser.add_argument('--addRoot', help='Add new image root directory.')

    args = parser.parse_args()  
    dbName = params['params']['photoDatabase']['fileName']

    ## Connect to the database. Also set up Ctrl-C Handling
    conn = sqlite3.connect(os.path.join(project_path, 'databases', dbName))
    conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")

    def signal_handler(signal, frame):
        proc.kill()
        conn.commit()
        conn.close()
        print "Going down!"
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    rootDirRows = getRoots(conn, args, params)

    # rootDirRows = {}
    # rootDirRows['/mnt/NAS/Jessica Pictures'] = 2

    print rootDirRows
    # print rootDirRows.keys()[rootDirRows.values().index(2)] 

    # Reverse rootDirRows for key to dir translation
    # rootDirReverse = {}
    # for key in rootDirRows.keys():
    #     print key
    #     val = rootDirRows[key]
    #     rootDirReverse[val] = key

    photoTableName = params['params']['photoDatabase']['tables']['photoTable']['Name']
    photoCols = params['params']['photoDatabase']['tables']['photoTable']['Columns']
    photoFileCol = photoCols['photoFile']
    modDateCol = photoCols['modifyDate']
    rootDirCol = photoCols['rootDirNum']

    photoInTableQuery = '''SELECT {}, {}, {} FROM {}'''.format(photoFileCol, modDateCol, rootDirCol, photoTableName)

    def dict_factory(cursor, row):
        d = dict()
        # Formats the return of a result so that we get a fullpath and a moddate in a dictionary.

        for idx, col in enumerate(cursor.description):
            filename = row[0]
            modDate = row[1]
            rootDirKey = row[2]
            rootDir = rootDirRows.keys()[rootDirRows.values().index(rootDirKey)] 
            fullpath = os.path.join(rootDir, filename)
            d[fullpath] = modDate
        return d

    conn.row_factory = dict_factory
    cc = conn.cursor()
    cc.execute(photoInTableQuery)
    result = cc.fetchone()

    dateDict = {}

    while result != None:
        fullpath = result.keys()[0]
        modDate = result[fullpath]
        dateDict[fullpath] = modDate
        result = cc.fetchone()
        # print fullpath + " " + modDate
    # IMPORTANT! Set the row factory for the database. 
    conn.row_factory = sqlite3.Row

    rootSubdirs = getUniqueSubDirs( list(rootDirRows.keys() ) )

    personNameDict = {}

    filesProcessed = 0

    for eachRoot in list(rootDirRows.keys() ):
        print eachRoot
        rootDirKey = rootDirRows[eachRoot]
        subdirs = sorted(rootSubdirs[eachRoot])

        print subdirs
        for eachDirectory in subdirs:
            files = os.listdir(os.path.join(eachRoot, eachDirectory) )
            for eachFile in files:
                filesProcessed += 1
                filepath = os.path.join(eachRoot, eachDirectory, eachFile);
                # print ('TODO: Check filepath in dict and stuff...')
                last_modified_date = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(filepath)))
                # Using the dateDict, we try to prevent a read to the database for every single file
                # just to see if it's up to date. Instead, we check dateDict and see if the modification
                # date is acceptable. If not, or it doesn't exist, we go ahead and add the photo using
                # the addPhoto function. Checking whether the file is in the dict is quite a bit faster. 
                if filepath in dateDict and (dateDict[filepath] >= last_modified_date):
                    pass
                else:
                    # try:
                    photoHandler.addPhoto(eachRoot, os.path.join(eachDirectory, eachFile), rootDirKey, params, conn, personNameDict)
                    # except Exception as e:
                    #     print "Error! " + str(e)
                    #     raise e
                    #     exit(1)
                if filesProcessed % 500 == 0 and filesProcessed > 0:
                    print "{} files processed already.".format(filesProcessed)

    photoHandler.checkPhotosAtEnd(conn, params)

    proc.terminate()



# for root, dirs, files in os.walk(dirB):
#     for name in files:
#         print(os.path.join(root, name))
#     for name in dirs:
#         print(os.path.join(root, name))
