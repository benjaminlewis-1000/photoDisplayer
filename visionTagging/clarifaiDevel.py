#! /usr/bin/env python

from clarifai.rest import ClarifaiApp

import classImage

import argparse
import datetime
import os
import pyexiv2
import re
import sqlite3
import tkFileDialog
from Tkinter import *
import time
from time import gmtime, strftime
import json
import signal
import sys
import yaml

def signal_handler(signal, frame):
	resetCountQuery = '''UPDATE ''' + yParams['visionMetaTableName'] + ''' SET Value = ? WHERE Name = ?'''
	c.execute(resetCountQuery, (alreadyDone, yParams['visionMetaClarifaiReadsThisMonth']) )
	print "you did it!"
	conn.commit()
	conn.close()
	sys.exit(0)

## A method to read the database and find out how many reads per month we want to do with Clarifai.
## Returns the number of reads already performed this month, the max reads per month, and resets
## the month definitions if a new billing month has occurred. 
def setUpLimitsClarifai(conn, params):
	c = conn.cursor()
	### Get all the parameters from the appropriate table in the database
	metadataQuery = '''SELECT * FROM ''' + params['visionMetaTableName']
	c.execute(metadataQuery )

	## Read all parameters into a dictionary. 
	dbMetadata = c.fetchall()
	metadataDict = {}
	for i in range(len(dbMetadata)):
		metadataDict[dbMetadata[i][0]] = dbMetadata[i][1]

	## Self-explanatory
	readsPerMonth = metadataDict[params['visionMetaClarifaiReadsPerMonth']]
	readsThisMonth = metadataDict[params['visionMetaClarifaiReadsThisMonth']]
	newMonthDate = metadataDict[params['visionMetaClarifaiNewMonthDate']]
	dateLastRead = metadataDict[params['visionMetaClarifaiDayLastRead']]
	dayOfNewMonth = metadataDict[params['visionMetaClarifaiDayOfNewMonth']]
	todayDate = strftime("%Y-%m-%d", gmtime())
	now = datetime.datetime.now()

	## If we have hit a new month, then reset the month for a new date using date math and
	## store that in the database. 
	if todayDate > newMonthDate:
		readsThisMonth = 0
		if now.day > dayOfNewMonth:
			renewMonth = str(format(now.month % 12 + 1, '02') )
			renewYear = str(now.year + int(now.month / 12))
			renewDate = str(renewYear + "-" + renewMonth + "-" + str(dayOfNewMonth))
		else:
			renewDate = str(str(now.year) + "-" + str(format(now.month, '02') ) + "-" + str(dayOfNewMonth))

		renewDateQuery = '''UPDATE ''' + params['visionMetaTableName'] + ''' SET Value = ? WHERE Name = ?'''
		c.execute(renewDateQuery, (renewDate, params['visionMetaClarifaiNewMonthDate']) )
		resetCountQuery = '''UPDATE ''' + params['visionMetaTableName'] + ''' SET Value = 0 WHERE Name = ?'''
		c.execute(resetCountQuery, (params['visionMetaClarifaiReadsThisMonth'],) )

		conn.commit()

	return( (readsThisMonth, readsPerMonth ) )

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Tag images using the Clarifai vision API (see clarifai.com). Inputs can include a directory; otherwise, a pop-up window will ask for a root directory to scan.')
	parser.add_argument('--root', help='Root directory of the images to scan.')
	parser.add_argument('--doDeep', help="Doesn't use the indexed files in the database to skip already read files; tends to run slower.")

	args = parser.parse_args()

	## Open the API Key file and read the app ID and app secret.
	api_file = open('clarifaiAPIkey.key', 'r')
	app_id = api_file.readline().rstrip("\n\r")
	app_secret = api_file.readline()
	api_file.close()

	# Get the current date and time
	currentTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

	## Open the params.yaml file for the configuration parameters
	with open('../config/params.yaml') as stream:
		try:
			yParams = yaml.load(stream)
		except yaml.YAMLError as exc:
			print(exc)
			exit(1)

	## Connect to the database. Also set up Ctrl-C Handling
	conn = sqlite3.connect("visionDatabase.db")
	signal.signal(signal.SIGINT, signal_handler)

	## Use the method above to find the number of monthly reads we want from Clarifai
	## and the number that have already been done this month.
	limits = setUpLimitsClarifai(conn, yParams)
	monthlyLimit = limits[1]
	alreadyDone = limits[0]

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
	getConfirmedFilesQuery = "SELECT " + yParams['visionRecordFileColumn'] + " FROM " + yParams['visionRecordDataTableName'] + " WHERE " + yParams['visionRecordValidColumn'] + " = 1 AND " + yParams['visionRecordSourceColumn'] + " = ?"
	c.execute(getConfirmedFilesQuery, (classImage.clarifaiLabelTuple[0],) )
	results = c.fetchall()
	readFiles = []
	for i in range(len(results)):
		readFiles.append( str(results[i][0]) )


	## List all the files in the root directory that end with JPEG-type file formats.
	## Add them to a list. 
	listAllFiles = []
	for dirpath, dirnames, filenames in os.walk(rootDirectory):
		for fname in filenames:
			if fname.endswith(tuple([".JPG", ".jpg", ".jpeg", ".JPEG"])):
				if args.doDeep != None:
					listAllFiles.append(os.path.join(dirpath, fname))
				else:
					if os.path.join(dirpath, fname) not in readFiles:
						listAllFiles.append(os.path.join(dirpath, fname))
					else:
						print fname + " is read already."


	for filename in listAllFiles:
		## Try-except block to classify the image with the API. In the event that we reach the monthly limit
		## or have some exception, we save off the new number of files processed and exit the loop.
		try:
			clarifaiVal = classImage.classifyImageWithClarifaiAPI(filename, app_id, app_secret, conn, currentTime)
		except IOError as ioe:
			print "IO Error in clarifai classify: " + str(ioe)
			clarifaiVal = 0
			logfile = open('logErrata.out', 'a')
			print >>logfile, "File " + filename + " was not able to open for classification in Clarifai."
			logfile.close()
		except Exception as e:
<<<<<<< HEAD
			print "Previously unknown exception: " +  str(e)
			print "Breaking."
=======
			print "Error: " + str(e)
>>>>>>> origin/master
			resetCountQuery = '''UPDATE ''' + yParams['visionMetaTableName'] + ''' SET Value = ? WHERE Name = ?'''
			c.execute(resetCountQuery, (alreadyDone, yParams['visionMetaClarifaiReadsThisMonth']) )
			conn.commit()
			break

		alreadyDone += clarifaiVal

		if alreadyDone == monthlyLimit:
			print "Monthly limit has been reached."
			resetCountQuery = '''UPDATE ''' + yParams['visionMetaTableName'] + ''' SET Value = ? WHERE Name = ?'''
			c.execute(resetCountQuery, (alreadyDone, yParams['visionMetaClarifaiReadsThisMonth']) )
			conn.commit()
			break


	conn.commit()
	conn.close()
