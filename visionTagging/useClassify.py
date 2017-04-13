#! /usr/bin/python

import classImage

import argparse
import datetime
import json
import os
import pyexiv2
import re
import signal
import sqlite3
import sys
import tkFileDialog
from Tkinter import *
import time
from time import gmtime, strftime
import yaml

def signal_handler(signal, frame):
	print "you did it!"
	conn.commit()
	conn.close()
	sys.exit(0)


## A method to read the database and find out how many reads per month we want to do with Clarifai.
## Returns the number of reads already performed this month, the max reads per month, and resets
## the month definitions if a new billing month has occurred. 
def setUpLimitsGoogle(conn, params):
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
	readsPerMonth = metadataDict[params['visionMetaGoogleReadsPerMonth']]
	readsThisMonth = metadataDict[params['visionMetaGoogleReadsThisMonth']]
	newMonthDate = metadataDict[params['visionMetaGoogleNewMonthDate']]
	dateLastRead = metadataDict[params['visionMetaGoogleDayLastRead']]
	dayOfNewMonth = metadataDict[params['visionMetaGoogleDayOfNewMonth']]
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
		c.execute(renewDateQuery, (renewDate, params['visionMetaGoogleNewMonthDate']) )
		resetCountQuery = '''UPDATE ''' + params['visionMetaTableName'] + ''' SET Value = 0 WHERE Name = ?'''
		c.execute(resetCountQuery, (params['visionMetaGoogleReadsThisMonth'],) )

		conn.commit()

	return( (readsThisMonth, readsPerMonth ) )


def wipeImage(filename):
	metadata = pyexiv2.ImageMetadata(filename)
	metadata.read()
	if imageHistoryField in metadata:
		metadata[imageHistoryField].value = ""
	if commentField in metadata:
		metadata[commentField].value = ""


	isUnlocked = os.access(filename, os.W_OK)
	while not isUnlocked:
		sleep(0.1)
	try:
		# print "File " + filename + " exists? : " + str(os.path.isfile(filename))
		metadata.write()
	except Exception as e:
		print "Exception in writing metdata: Not written. Method wipeImage"
		print "More info: " + str(e)

	rmDBcommand = '''DELETE FROM visionData where filename = "''' + filename + "\""
	c = conn.cursor()
	c.execute(rmDBcommand)



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Tag images using the Google Vision API (see https://cloud.google.com/vision/). Inputs can include a directory; otherwise, a pop-up window will ask for a root directory to scan.')
	parser.add_argument('--root', help='Root directory of the images to scan.')
	parser.add_argument('--doDeep', help="Doesn't use the indexed files in the database to skip already read files; tends to run slower.")

	args = parser.parse_args()

	## Open the API Key file and read the Google Vision App password
	api_file = open('googAPIkey.key', 'r')
	api_key = api_file.read().rstrip("\n\r")
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
	limits = setUpLimitsGoogle(conn, yParams)
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

	

### Get the current time and connect to the database that lets 
### us know if we've already processed the image. 


# dir = 'C:\\Users\\Benjamin\\Dropbox\\Perl Code\\photoDisplayer\\base'
rootDirectory = 'D:\Pictures\\Family Pictures'

listAllFiles = []
ext = [".JPG", ".jpg", ".jpeg", ".JPEG"]

for dirpath, dirnames, filenames in os.walk(rootDirectory):
	for fname in filenames:
		if fname.endswith(tuple(ext)):
			listAllFiles.append(os.path.join(dirpath, fname))





# testImage = 'D:\Pictures\\2016\Ohio\\adulting (1).jpg'



# rval = classImage.classifyOneImageGoogleAPI(api_key, 'D:\Pictures\\2016\Ohio\\adulting (1).jpg')
# print rval
# readInfo("D:/Pictures/2016/Chicago and Wicked/wicked_south_bend (2).jpg")



t1 = time.time()

for file in listAllFiles:
	readInfo(file)
	print file
	# classImage.classifyImageWithGoogleAPI(goog_api_key, file, conn, curTime)

t2 = time.time()

print "Finished all files! Seconds: " + str(t2 - t1) + " for " + str( len(listAllFiles) ) + " files."


conn.commit()
conn.close()


### TODO ### 
"""
	- Make sure you aren't redoing a file if it hasn't been rotated or if we have already done it
	- If we are redoing a file, erase the tags from the method first

"""


	# print val
	# if 'labelAnnotations' in val:
	# 	labelIterator = val['labelAnnotations']
	# 	for label in labelIterator:
	# 		print label

	# if 'landmarkAnnotations' in val:
	# 	pass