#! /usr/bin/python

import classImage

import yaml
import datetime
import os
import pyexiv2 as pe2
import re
import sqlite3
from time import gmtime, strftime
import json

import signal
import sys

def signal_handler(signal, frame):
	print "you did it!"
	conn.commit()
	conn.close()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

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
dir = 'D:\Pictures\\2016'

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


for file in listAllFiles:
	classImage.classifyImageWithGoogleAPI(api_key, file, conn, curTime)

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
# clearImage(testImage)
# classImage.classifyImageWithGoogleAPI(api_key, testImage, conn, curTime)

# print "Out and about"
# # print "Needs to be done = " + str(classImage.decideIfNeedToDo(testImage, classImage.googleLabelTuple, conn, curTime))

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