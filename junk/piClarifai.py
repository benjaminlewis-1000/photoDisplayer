#! /usr/bin/env python

print "Starting..."

from clarifai.rest import ClarifaiApp

import classImage

import datetime
import os
import pyexiv2
import re
import sqlite3
import time
from time import gmtime, strftime
import json
import signal
import sys
import yaml


def signal_handler(signal, frame):
	resetCountQuery = '''UPDATE ''' + yParams['visionMetaTableName'] + ''' SET Value = ? WHERE Name = ?'''
	c.execute(resetCountQuery, (alreadyDone, yParams['visionMetaReadsThisMonth']) )
	print "you did it!"
	conn.commit()
	conn.close()
	sys.exit(0)


api_file = open('clarifaiAPIkey.key', 'r')
app_id = api_file.readline().rstrip("\n\r")
app_secret = api_file.readline()
api_file.close()

with open('../config/params.yaml') as stream:
	try:
		yParams = yaml.load(stream)
	except yaml.YAMLError as exc:
		print(exc)

# file = "D:\Users\Benjamin\\testimage1.JPG"
# file = "N:\Photos\Erica's Pictures\January 2009\PICT0463.JPG"
# ctxt = base64Encode(file)

conn = sqlite3.connect("visionDatabase.db")
signal.signal(signal.SIGINT, signal_handler)

currentTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
# get the general model

def setUpLimitsClarifai():
	c = conn.cursor()
	metadataQuery = '''SELECT * FROM ''' + yParams['visionMetaTableName']
	c.execute(metadataQuery )

	# readsPerMonth = 0
	# readsThisMonth = 0
	# newMonthDate = 1
	# dayLastRead = 2
	# dayOfNewMonth = 1

	dbMetadata = c.fetchall()
	metadataDict = {}
	for i in range(len(dbMetadata)):
		metadataDict[dbMetadata[i][0]] = dbMetadata[i][1]

	readsPerMonth = metadataDict[yParams['visionMetaReadsPerMonth']]
	readsThisMonth = metadataDict[yParams['visionMetaReadsThisMonth']]
	newMonthDate = metadataDict[yParams['visionMetaNewMonthDate']]
	dateLastRead = metadataDict[yParams['visionMetaDayLastRead']]
	dayOfNewMonth = metadataDict[yParams['visionMetaDayOfNewMonth']]
	todayDate = strftime("%Y-%m-%d", gmtime())
	now = datetime.datetime.now()

	if todayDate > newMonthDate:
		readsThisMonth = 0
		print "Tr"
		if now.day > dayOfNewMonth:
			renewMonth = str(format(now.month % 12 + 1, '02') )
			renewYear = str(now.year + int(now.month / 12))
			renewDate = str(renewYear + "-" + renewMonth + "-" + str(dayOfNewMonth))
		else:
			renewDate = str(str(now.year) + "-" + str(format(now.month, '02') ) + "-" + str(dayOfNewMonth))

		renewDateQuery = '''UPDATE ''' + yParams['visionMetaTableName'] + ''' SET Value = ? WHERE Name = ?'''
		c.execute(renewDateQuery, (renewDate, yParams['visionMetaNewMonthDate']) )
		resetCountQuery = '''UPDATE ''' + yParams['visionMetaTableName'] + ''' SET Value = 0 WHERE Name = ?'''
		c.execute(resetCountQuery, (yParams['visionMetaReadsThisMonth'],) )

		conn.commit()

	return( (readsThisMonth, readsPerMonth ) )



limits = setUpLimitsClarifai()
monthlyLimit = limits[1]
alreadyDone = limits[0]

rootDirectory = '/mnt/NAS/Photos'

listAllFiles = []
ext = [".JPG", ".jpg", ".jpeg", ".JPEG"]

for dirpath, dirnames, filenames in os.walk(rootDirectory):
	for fname in filenames:
		if fname.endswith(tuple(ext)):
			listAllFiles.append(os.path.join(dirpath, fname))

c = conn.cursor()

for filename in listAllFiles:
	try:
		clarifaiVal = classImage.classifyImageWithClarifaiAPI(filename, app_id, app_secret, conn, currentTime)
		alreadyDone += clarifaiVal
		print alreadyDone
		if alreadyDone >= monthlyLimit:
			print "True"
			resetCountQuery = '''UPDATE ''' + yParams['visionMetaTableName'] + ''' SET Value = ? WHERE Name = ?'''
			c.execute(resetCountQuery, (alreadyDone, yParams['visionMetaReadsThisMonth']) )
			conn.commit()
			classImage.classifyImageWithClarifaiAPI(filename, app_id, app_secret, conn, currentTime)
			print "Reached the monthly limit!"
			break
 	except:
 		print "Catching!"
 		resetCountQuery = '''UPDATE ''' + yParams['visionMetaTableName'] + ''' SET Value = ? WHERE Name = ?'''
 		c.execute(resetCountQuery, (alreadyDone, yParams['visionMetaReadsThisMonth']) )
 		conn.commit()
# # tags = clarifaiClassify(file, app_id, app_secret )

# print tags
# classImage.classifyImageWithClarifaiAPI(file, app_id, app_secret, conn, curTime )

conn.commit()
conn.close()
