#! /usr/bin/env python

from clarifai.rest import ClarifaiApp

import classImage

import argparse
import datetime
import os
import pyexiv2
import re
from requests.exceptions import SSLError, ConnectionError
import sqlite3
import tkFileDialog
from Tkinter import *
import time
from time import gmtime, strftime, sleep
import traceback
import json
import signal
import sys
import yaml
from clarifai.rest.client import ApiError
import xmltodict

def signal_handler(signal, frame):
    resetCountQuery = '''UPDATE ''' + visionMetaTableName + ''' SET Value = ? WHERE Name = ?'''


    if method == 'clarifai':
        readsThisMonthField = params['params']['visionTaggingParams']['database']['Fields']['clarifaiFields']['ReadsThisMonth']
        c.execute(resetCountQuery, (alreadyDone, readsThisMonthField) )
    else:
        readsThisMonthField = params['params']['visionTaggingParams']['database']['Fields']['googFields']['ReadsThisMonth']
        c.execute(resetCountQuery, (alreadyDone, readsThisMonthField) )
    print "you did it!"
    conn.commit()
    conn.close()
    sys.exit(0)

## A method to read the database and find out how many reads per month we want to do with Clarifai.
## Returns the number of reads already performed this month, the max reads per month, and resets
## the month definitions if a new billing month has occurred. 
def setUpLimits(conn, params, method):
    c = conn.cursor()
    ### Get all the parameters from the appropriate table in the database
    visionMetaTableName = params['params']['visionTaggingParams']['database']['tables']['visionMetaTable']['Name']
    metadataQuery = '''SELECT * FROM ''' + visionMetaTableName
    c.execute(metadataQuery )

    ## Read all parameters into a dictionary. 
    dbMetadata = c.fetchall()
    metadataDict = {}
    for i in range(len(dbMetadata)):
        metadataDict[dbMetadata[i][0]] = dbMetadata[i][1]

    ## Self-explanatory
    if method == 'clarifai':
        fieldsVar = 'clarifaiFields'
    else:
        fieldsVar = 'googFields'

    fieldsBase = params['params']['visionTaggingParams']['database']['Fields']

    readsPerMonth = metadataDict[fieldsBase[fieldsVar]['ReadsPerMonth']]
    readsThisMonth = metadataDict[fieldsBase[fieldsVar]['ReadsThisMonth']]
    newMonthDate = metadataDict[fieldsBase[fieldsVar]['NewMonthDate']]
    dateLastRead = metadataDict[fieldsBase[fieldsVar]['DayLastRead']]
    dayOfNewMonth = metadataDict[fieldsBase[fieldsVar]['DayOfNewMonth']]

    print "Database - monthly Limit: " + str(readsPerMonth) + ", already done: " + str(readsThisMonth)

    todayDate = strftime("%Y-%m-%d", gmtime())
    now = datetime.datetime.now()

    ## If we have hit a new month, then reset the month for a new date using date math and
    ## store that in the database. 
    print "Today's date is: " + todayDate
    print "New month's date is : " + str(newMonthDate)
    if todayDate > newMonthDate:
        readsThisMonth = 0
        if now.day > dayOfNewMonth:
            renewMonth = str(format(now.month % 12 + 1, '02') )
            renewYear = str(now.year + int(now.month / 12))
            renewDate = str(renewYear + "-" + renewMonth + "-" + str(dayOfNewMonth))
        else:
            renewDate = str(str(now.year) + "-" + str(format(now.month, '02') ) + "-" + str(dayOfNewMonth))

        renewDateQuery = '''UPDATE ''' + visionMetaTableName+ ''' SET Value = ? WHERE Name = ?'''
        c.execute(renewDateQuery, (renewDate, fieldsBase[fieldsVar]['NewMonthDate']) )
        resetCountQuery = '''UPDATE ''' + visionMetaTableName + ''' SET Value = 0 WHERE Name = ?'''
        c.execute(resetCountQuery, (fieldsBase[fieldsVar]['ReadsThisMonth'],) )

        conn.commit()

    return( (readsThisMonth, readsPerMonth ) )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tag images using the Clarifai vision API (see clarifai.com). Inputs can include a directory; otherwise, a pop-up window will ask for a root directory to scan.')
    parser.add_argument('--root', help='Root directory of the images to scan.')
    parser.add_argument('--doDeep', help="Doesn't use the indexed files in the database to skip already read files; tends to run    slower.")
    parser.add_argument('--method', help="Select methods. Valid values currently are 'google' or 'clarifai'.")  
    parser.add_argument('--debug_file', help="Debug input file.")
    parser.add_argument('--max_sec', help="Max time for method to run, in seconds.")

    args = parser.parse_args()  

    if args.method == 'clarifai':
        method = 'clarifai'
        print "Using method Clarifai"
    else:
        method = 'google' 
        print "Using method Google"

    if not args.max_sec:
        args.max_sec = 99999

    ## Open the API Key file and read the app ID and app secret.
    if method == 'clarifai':
        api_file = open(classImage.script_path + '/clarifaiAPIkey.key', 'r')
        app_id = api_file.readline().rstrip("\n\r")
        app_secret = api_file.readline()
        api_file.close()
    else:
        api_file = open(classImage.script_path + '/googAPIkey.key', 'r')
        api_key = api_file.read().rstrip("\n\r")
        api_file.close()


	# Get the current date and time
    currentTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

	## Open the params.yaml file for the configuration parameters
    with open(classImage.project_path + '/config/params.xml') as stream:
        try:
            params = xmltodict.parse(stream.read())
        except Exception as exc:
            print(exc)
            exit(1)

    visionMetaTableName = params['params']['visionTaggingParams']['database']['tables']['visionMetaTable']['Name']

    ## Connect to the database. Also set up Ctrl-C Handling
    conn = sqlite3.connect(classImage.script_path + "/" + params['params']['visionTaggingParams']['database']['fileName'])
    conn.text_factory = str
    signal.signal(signal.SIGINT, signal_handler)

    ## Use the method above to find the number of monthly reads we want from Clarifai
    ## and the number that have already been done this month.
    limits = setUpLimits(conn, params, method)
    monthlyLimit = limits[1]
    alreadyDone = limits[0]

    print "Monthly Limit: " + str(monthlyLimit) + ", already done: " + str(alreadyDone)

    ## Find the root directory that we want to scan. Either it was passed in
    ## as an arg with --root <directory>, or we launch a file dialog to
    ## get the directory. 
    if args.root != None and os.path.isdir(args.root):
        rootDirectory = args.root
    else:
        rootWindow = Tk()
        rootWindow.withdraw()
        rootDirectory = tkFileDialog.askdirectory()

    c = conn.cursor()
    recordColumn = params['params']['visionTaggingParams']['database']['tables']['recordDataTable']['Columns']['File']
    recordTableName = params['params']['visionTaggingParams']['database']['tables']['recordDataTable']['Name']
    validityColumn = params['params']['visionTaggingParams']['database']['tables']['recordDataTable']['Columns']['Valid']
    sourceColumn = params['params']['visionTaggingParams']['database']['tables']['recordDataTable']['Columns']['Source']
    getConfirmedFilesQuery = "SELECT " + recordColumn + " FROM " + recordTableName + " WHERE " + validityColumn + " = 1 AND " + sourceColumn + " = ?"
    if method == 'clarifai':
        c.execute(getConfirmedFilesQuery, (classImage.clarifaiLabelTuple[0],) )
    else:
        c.execute(getConfirmedFilesQuery, (classImage.googleLabelTuple[0],) )
    results = c.fetchall()
    readFiles = set()
    for i in range(len(results)):
        readFiles.add( str(results[i][0]) )

    with open(classImage.script_path + '/landmarkKeywords.txt') as f:
        knownWords = f.read().splitlines()

    if args.debug_file != None:
        print "Debugging..."
        listAllFiles = (args.debug_file,)

    else:

	## List all the files in the root directory that end with JPEG-type file formats.
	## Add them to a list. 
        setOfFiles = set()
        for dirpath, dirnames, filenames in os.walk(rootDirectory):
            for fname in filenames:
                if fname.endswith(tuple([".JPG", ".jpg", ".jpeg", ".JPEG"])):
                    setOfFiles.add(os.path.join(dirpath, fname))
                # if args.doDeep != None:
                #     listAllFiles.append(os.path.join(dirpath, fname))
                # else:
                #     if os.path.join(dirpath, fname) not in readFiles:
                #         listAllFiles.append(os.path.join(dirpath, fname))
                #     else:
                #         readFiles.remove(os.path.join(dirpath, fname))

    # setOfFiles = setOfFiles - readFiles
        listAllFiles = list(setOfFiles - readFiles)

    if method == 'clarifai':
        readsThisMonthField = params['params']['visionTaggingParams']['database']['Fields']['clarifaiFields']['ReadsThisMonth']
    else:
        readsThisMonthField = params['params']['visionTaggingParams']['database']['Fields']['googFields']['ReadsThisMonth']


    print "Length to do: " + str(len(listAllFiles))

    start_time = time.time()
    for filename in listAllFiles:

        metadata = pyexiv2.ImageMetadata(filename)
        metadata.read()
        dateTakenOrig = metadata['Exif.Photo.DateTimeOriginal'].raw_value
        dateTaken = metadata['Exif.Photo.DateTime'].raw_value
        successVal = 0
		## Try-except block to classify the image with the API. In the event that we reach the monthly limit
		## or have some exception, we save off the new number of files processed and exit the loop.
        try:
            if method == 'clarifai':
                successVal = classImage.classifyImageWithClarifaiAPI(filename, app_id, app_secret, conn, currentTime)
            else:
                successVal = classImage.classifyImageWithGoogleAPI(api_key, filename, conn, currentTime, knownWords)
            elapsed_time = time.time() - start_time

            if int(elapsed_time) > int(args.max_sec):
                print "Time specified ({} seconds) has elapsed. Exiting.".format(args.max_sec)
                setCountQuery = '''UPDATE ''' + visionMetaTableName + ''' SET Value = ? WHERE Name = ?'''
                c.execute(setCountQuery, (alreadyDone, readsThisMonthField ) )
                conn.commit()

                metadata = pyexiv2.ImageMetadata(filename)
                metadata.read()
                metadata['Exif.Photo.DateTimeOriginal'] = dateTakenOrig
                metadata['Exif.Photo.DateTime'] = dateTaken
                metadata.write()
                
                break

        except IOError as ioe:
            print "IO Error in clarifai classify: " + str(ioe)
            successVal = 0
            logfile = open(classImage.script_path + '/logErrata.out', 'a')
            print >>logfile, "Clarifai - IO Error in file " + filename + " (most likely caused by inability to open) : " + str(type(ioe)) + ",  " + str(ioe.args) + ",  " + str(ioe)
            logfile.close()

        except AttributeError as ae:
            print "AttributeError: " + str(ae)
            successVal = 0
            sleep(60)

        except (SSLError, ConnectionError) as ssle:
            successVal = 0
            print "SSL Error: " + str(ssle)
            sleep(60)
        except ApiError as apie:

            # Try to see if we are out of funds (For Clarifai)
            outOfFunds = re.search(r"limits exceeded", str(apie) )
            if outOfFunds:
                print "Out of funds! Exiting..."
                setCountQuery = '''UPDATE ''' + visionMetaTableName + ''' SET Value = ? WHERE Name = ?'''
                c.execute(setCountQuery, (alreadyDone, readsThisMonthField ) )
                conn.commit()
                break

            print "Clarifai API error..." + str(apie)
            sleep(60)

        except Exception as e:

            print "Stack trace: " 
            traceback.print_exc()
            successVal = 0

            # Get detailed info about the exception and print it out. 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            
            print "Previously unknown exception: " +  str(e)
            print "Breaking."
            print "Error: " + str(e)
            resetCountQuery = '''UPDATE ''' + visionMetaTableName + ''' SET Value = ? WHERE Name = ?'''
            c.execute(resetCountQuery, (alreadyDone, readsThisMonthField) )
            conn.commit()
            logfile = open(classImage.script_path + '/logErrata.out', 'a')
            print >>logfile, method + " - error in file " + filename + ": " + str(type(e)) + ",  " + str(e.args) + ",  " + str(e)
            logfile.close()

            metadata = pyexiv2.ImageMetadata(filename)
            metadata.read()
            metadata['Exif.Photo.DateTimeOriginal'] = dateTakenOrig
            metadata['Exif.Photo.DateTime'] = dateTaken
            metadata.write()

            break

        finally:
            alreadyDone += successVal
            if successVal:
                print "We have done " + str(alreadyDone) + " pictures this month now."

            metadata = pyexiv2.ImageMetadata(filename)
            metadata.read()
            metadata['Exif.Photo.DateTimeOriginal'] = dateTakenOrig
            metadata['Exif.Photo.DateTime'] = dateTaken
            metadata.write()

        if alreadyDone == monthlyLimit:
            print "Monthly limit has been reached."
            resetCountQuery = '''UPDATE ''' + visionMetaTableName + ''' SET Value = ? WHERE Name = ?'''
            c.execute(resetCountQuery, (alreadyDone, readsThisMonthField) )
            conn.commit()
            break

    conn.commit()
    conn.close()
