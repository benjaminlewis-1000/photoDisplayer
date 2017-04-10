#! /usr/bin/python

import classImage

import yaml
import datetime
import os
import pyexiv2 as pe2
import re
import sqlite3
import time
from time import gmtime, strftime
import json

import signal
import sys

def readInfo(filename):
	metadata = pe2.ImageMetadata(filename)
	metadata.read()
	if imageHistoryField in metadata:
		imageHistory =  metadata[imageHistoryField].raw_value
		print "Image history: " + imageHistory + "\n"
	if commentField in metadata:
		comments =  metadata[commentField].raw_value
		print "Comments: " + comments + "\n"
		historyMatch = re.search(r'UUUUU' , comments)

		if (historyMatch):
			print "Found something!"

	decision = classImage.decideIfNeedToDo(filename, classImage.googleLabelTuple, conn, curTime)
	print decision

def signal_handler(signal, frame):
	print "you did it!"
	conn.commit()
	conn.close()
	sys.exit(0)

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

signal.signal(signal.SIGINT, signal_handler)

# wipeImage("")

### INVESTIGATE::: D:\Pictures\2016\Ohio\adulting (1).jpg

### Define a short version of the metadata fields we will be using. 
picasaTagField = 'Iptc.Application2.Keywords'
imageHistoryField = 'Exif.Image.ImageHistory'
commentField = 'Exif.Photo.UserComment'


### Get YAML parameters for field names.
with open('../config/params.yaml') as stream:
	try:
		yParams = yaml.load(stream)
	except yaml.YAMLError as exc:
		print(exc)

### Get the current time and connect to the database that lets 
### us know if we've already processed the image. 

curTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# dir = 'C:\\Users\\Benjamin\\Dropbox\\Perl Code\\photoDisplayer\\base'
dir = 'D:\Pictures\\Family Pictures'

listAllFiles = []
ext = [".JPG", ".jpg", ".jpeg", ".JPEG"]

for dirpath, dirnames, filenames in os.walk(dir):
	for fname in filenames:
		if fname.endswith(tuple(ext)):
			listAllFiles.append(os.path.join(dirpath, fname))


conn = sqlite3.connect("visionDatabase.db")


api_file = open('googAPIkey.key', 'r')
api_key = api_file.read()
api_file.close()

# testImage = 'D:\Pictures\\2016\Ohio\\adulting (1).jpg'



# rval = classImage.classifyOneImageGoogleAPI(api_key, 'D:\Pictures\\2016\Ohio\\adulting (1).jpg')
# print rval
# readInfo("D:/Pictures/2016/Chicago and Wicked/wicked_south_bend (2).jpg")



t1 = time.time()

for file in listAllFiles:
	readInfo(file)
	print file
	# classImage.classifyImageWithGoogleAPI(api_key, file, conn, curTime)

t2 = time.time()

print "Finished all files! Seconds: " + str(t2 - t1) + " for " + str( len(listAllFiles) ) + " files."

# def clearImage(filename):
# 	metadata = pe2.ImageMetadata(testImage)
# 	metadata.read()
# 	metadata[imageHistoryField] = ""
# 	metadata[commentField] = ""
# 	metadata.write()


# def simulateImage(filename):
# 	infile = open('out.out', 'rb')
# 	val = infile.read()
# 	infile.close()

# 	jsonVal =  json.loads(val)[0]
# 	classImage.tagPhotoFromGoogleJSON(filename, jsonVal, curTime, classImage.googleLabelTuple)

# clearDBquery = '''DELETE FROM visionData'''
# c = conn.cursor()
# c.execute(clearDBquery)
# conn.commit()


# testImage = 'C:\\Users\\Benjamin\\Dropbox\\Perl Code\\photoDisplayer\\base\\dirA\\awes.jpg'
# # clearImage(testImage)
# # classImage.classifyImageWithGoogleAPI(api_key, testImage, conn, curTime)

# # print "Out and about"
# print "Needs to be done = " + str(classImage.decideIfNeedToDo(testImage, classImage.googleLabelTuple, conn, curTime))

# # simulateImage(testImage)

# metadata = pe2.ImageMetadata(testImage)
# metadata.read()

# print curTime

# print "Image history: " + str(metadata[imageHistoryField].raw_value) + "\n"
# print "Comments: " + str(metadata[commentField].raw_value) + "\n"

# imageHistory = metadata['Exif.Image.ImageHistory'].raw_value

# # regexString = "(.*)" + "(\d+-\d+\d+ \d+:\d+:\d+), orientation is (\d)."
# # historyMatch = re.search(r"" + regexString + "" , imageHistory)

conn.commit()
conn.close()
# removePreviousTags(testImage)


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