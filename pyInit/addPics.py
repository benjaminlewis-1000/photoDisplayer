#! /usr/bin/env python

import os
import re
import sqlite3
import xmltodict
import argparse
from Tkinter import Tk
import tkMessageBox
from tkFileDialog import askdirectory

import vars

project_path = os.path.abspath(os.path.join(__file__,"../.."))
script_path  = os.path.abspath(os.path.join(__file__,".."))

def isSubDir(compDir, possibleSubDir):
    # print compDir
    # print possibleSubDir
    if re.search(r''+compDir, possibleSubDir) is None:
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

        rootDirRows[thisOSPath] = keyVal

        row = c.fetchone()

    if args.addRoot:

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
                acceptedVal = tkMessageBox.askquestion("Exit", "{} directory: {}".format(vars.osType, newDirName), icon='warning')

        isNewDirValid = os.path.isdir(newDirName) # Should be true if it's a directory
        for root in list(rootDirRows.keys()):
            if isSubDir(root, newDirName):
                isNewDirValid = False

        if isNewDirValid:
            newRootQuery = '''INSERT INTO {} ({}) VALUES (?) '''.format(rootTable, rootPathFieldName)

            try:
                c.execute(newRootQuery, (newDirName,))
                conn.commit()
            except sqlite3.OperationalError as oe:
                print "Operational error: " + str(oe)
                print "Problem query:     " + str(newRootQuery)
                print "Exiting. \n"
                exit(1)

            # Get the root key of the new directory
            rootKeyQuery = '''SELECT {} FROM {} WHERE {} = ?'''.format(rootKeyField, rootTable, rootPathFieldName)
            c.execute(rootKeyQuery, (newDirName,))
            row = c.fetchone()
            rootKey = row[0]
            rootDirRows[newDirName] = rootKey

    return rootDirRows


def getUniqueSubDirs(rootsList):
    subDirsDict = dict()
    for eachRoot in rootsList:
        currentSubDirs = []
        for root, dirs, files in os.walk(eachRoot):
            currentSubDirs.append(root)
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
                    currentSubDirs = list(set(currentSubDirs) - set(currentSubDirs).intersection(set(otherSubDirs)) )

        subDirsDict[currentRoot] = currentSubDirs

    return subDirsDict


if __name__ == '__main__':

    ## Open the params.xml file for the configuration parameters
    with open(os.path.join(project_path, 'config/params.xml') ) as stream:
        try:
            params = xmltodict.parse(stream.read())
        except Exception as exc:
            print(exc)
            exit(1)

    parser = argparse.ArgumentParser(description='Python version of the photo display program.')
    parser.add_argument('--addRoot', action='store_true', help='Add new image root directory.')

    args = parser.parse_args()  
    dbName = params['params']['photoDatabase']['fileName']

    ## Connect to the database. Also set up Ctrl-C Handling
    conn = sqlite3.connect(os.path.join(project_path, 'databases', dbName))
    conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")

    rootDirRows = getRoots(conn, args, params)
    print rootDirRows

    rootSubdirs = getUniqueSubDirs( list(rootDirRows.keys() ) )

    for eachRoot in list(rootDirRows.keys() ):
        key = rootDirRows[eachRoot]
        subdirs = rootSubdirs[eachRoot]

# for root, dirs, files in os.walk(dirB):
#     for name in files:
#         print(os.path.join(root, name))
#     for name in dirs:
#         print(os.path.join(root, name))