#! /usr/bin/env python

import os
import re
import sqlite3
import xmltodict
import argparse
from Tkinter import Tk
import Tkinter as tk
import tkMessageBox
from tkFileDialog import askdirectory
from time import sleep
import os
import subprocess

import signal
import time

import photoHandler

import vars
if vars.osType == vars.linuxType:
    import psutil
else:
    raise OSError('This hasn''t been tested on Windows.')

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

    if args.addRoot or args.addRootGUI or args.addRootParams:
        finishedRoots = False

        newRootsList = []

        if args.addRootGUI:
            root = tk.Tk()
            root.withdraw()
            while not finishedRoots:

                acceptedVal = 'No'
                while acceptedVal != 'yes':
                    # Get the home directory 
                    home = os.curdir      
                    if 'HOME' in os.environ:
                        home = os.environ['HOME']
                    elif os.name == 'posix':
                        home = os.path.expanduser("~/")
                    elif os.name == 'nt':
                        if 'HOMEPATH' in os.environ and 'HOMEDRIVE' in os.environ:
                            home = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
                    else:
                        home = os.environ['HOMEPATH']

                    dir_opt = {}
                    dir_opt['initialdir'] = home
                    newDirName = askdirectory(**dir_opt) # show an "Open" dialog box and return the path to the selected file
                    if newDirName == '':
                        window.option_add('*Dialog.msg.width', 20)
                        exitVal = tkMessageBox.askquestion("Confirmation", "Exit?", icon='warning')
                        if exitVal == 'yes':
                            exit(1)
                        window.option_add('*Dialog.msg.width', 75)
                    else:
                        acceptedVal = tkMessageBox.askquestion("Confirm", "Is " + vars.osType + " directory: "+ newDirName.encode('utf-8') + " acceptable?" , icon='warning')

                newRootsList.append(newDirName)

                continueVal = tkMessageBox.askquestion('Would you like to add more roots?', 'Would you like to add more roots?', icon='warning')
                finishedRoots = (continueVal == 'no')

        if args.addRoot:
            newRootsList.append(args.addRoot)

        if args.addRootParams:
            rootList = params['params']['mountDirs']
            for root in rootList['dir']:
                newRootsList.append(root)

        print newRootsList

        for newDirName in newRootsList:
            print "Adding root " + newDirName
            isdir = os.path.isdir(newDirName)
            isabsdir = os.path.isabs(newDirName)

            if not os.path.isabs(newDirName):
                newDirName = os.path.expanduser(newDirName)
                newDirName = os.path.abspath(newDirName)

            # print newDirName

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
        print eachRoot
        for root, dirs, files in os.walk( eachRoot.encode('utf8') ):
            # print root
            print root
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

    # geoServerIP =
    command = "ps aux | grep geoServer | grep -v grep | awk '{print $2}'"
    p = subprocess.Popen(command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        geoServerPID = int(p.stdout.read())
        os.system("kill {}".format(geoServerPID))
        noGeo = 0
    except ValueError as ve:
        noGeo = 1;

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
    if vars.osType == vars.linuxType:
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
    parser.add_argument('--addRootParams', action='store_true', help='Add new roots from the params.xml')
    parser.add_argument('--addRootGUI', action='store_true', help='Add new image root directory using a GUI.')
    parser.add_argument('--noPhotoAdd', action='store_true', help='Don\'t add photos to the directory; simply add the root directories.')

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

    if args.noPhotoAdd:
        # Don't need to do this right now. 
        # photoHandler.checkPhotosAtEnd(conn, params)
        exit(0)

    # rootDirRows = {}
    # rootDirRows['/mnt/NAS/Jessica Pictures'] = 2

    print "Root dir rows: " + str(rootDirRows)
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

    excludedDirectories = params['params']['excludeDirs']['dir']
    print "Excluded directories -- list comes from params : " + str(excludedDirectories)

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

    print "Done getting subdirectories!"

    personNameDict = {}
    tagDict = {}

    filesProcessed = 0


    for eachRoot in list(rootDirRows.keys() ):
        print eachRoot
        rootDirKey = rootDirRows[eachRoot]
        subdirs = sorted(rootSubdirs[eachRoot])

        # print "Subdirs: " +  str(subdirs)
        # print excludedDirectories
        for eachDirectory in subdirs:
            print eachDirectory
            eachDirectory = eachDirectory.decode('utf-8')
            # if eachDirectory in excludedDirectories:
            fullDirectory = os.path.join(eachRoot, eachDirectory)
            if any( list( fullDirectory.startswith(x) for x in excludedDirectories ) ):
                print "Not doing any files inside directory:"
                print fullDirectory 
            else:
#                 print "Adding files within directory {}".format(eachDirectory)
                # print eachDirectory
                files = os.listdir(os.path.join(eachRoot, eachDirectory) )
                for eachFile in files:
                    if eachFile.endswith(tuple([".JPG", ".jpg", ".jpeg", ".JPEG"]) ):
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
                            photoHandler.addPhoto(eachRoot, os.path.join(eachDirectory, eachFile), rootDirKey, params, conn, personNameDict, tagDict)
                            # try:
                            # except Exception as e:
                            #     print "Error! " + str(e)
                            #     raise e
                            #     exit(1)
                        if filesProcessed % 500 == 0 and filesProcessed > 0:
                            print "{} files processed already.".format(filesProcessed)
    
    print "Done adding..."
    photoHandler.checkPhotosAtEnd(conn, params)

    if vars.osType == vars.linuxType:
        proc.terminate()



# for root, dirs, files in os.walk(dirB):
#     for name in files:
#         print(os.path.join(root, name))
#     for name in dirs:
#         print(os.path.join(root, name))
