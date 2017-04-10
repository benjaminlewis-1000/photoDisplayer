#! /usr/bin/python

## Classify Unit Test

import classImage

import yaml
import datetime
import os
import pyexiv2
import re
import sqlite3
from time import gmtime, strftime, sleep
import json

import signal
import sys

dots = "........................................"
picasaTagField = 'Iptc.Application2.Keywords'
imageHistoryField = 'Exif.Image.ImageHistory'
commentField = 'Exif.Photo.UserComment'
conn = sqlite3.connect("visionDatabase.db")

errVal = False

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

def readInfo(filename):
	metadata = pyexiv2.ImageMetadata(filename)
	metadata.read()
	if imageHistoryField in metadata:
		imageHistory =  metadata[imageHistoryField].raw_value
		print "Image history: " + imageHistory 
	else:
		print "No image history"
	if commentField in metadata:
		comments =  metadata[commentField].raw_value
		print "Comments: " + comments 
		historyMatch = re.search(r'UUUUU' , comments)
		if (historyMatch):
			print "Found badly formed comments!"
	else:
		print "No comments."

print dots

# Define a test file, the database, and the current time.

file = "D:\Users\Benjamin\\testimage2.JPG"
wipeImage(file)
# D:\Pictures\Emily Wedding\\2015-08-18 05.33.01-1-1.jpeg


api_file = open('googAPIkey.key', 'r')
api_key = api_file.read()
api_file.close()

curTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

### Test 1: See if file needs to be API'd
needToUpdate = classImage.decideIfNeedToDo(file, classImage.googleLabelTuple, conn, curTime)
print "This file needs to be done: " + str(needToUpdate) + ". Should be: True"
if not needToUpdate:
	errVal = True

### Test 2: Check the metadata currently in the file
print dots + "\nGetting current metadata fields:"

readInfo(file)
print dots

### Test 3: Clearing comments

### Test 4: Classify with Google API
if 0:
	response = classImage.request_labels_and_landmarks_google(api_key, file)
	jsonResponse = json.loads(json.dumps(response.json()['responses']))[0]

	print jsonResponse
	print dots

	#### I know that this image has both labels and landmark data. Check that this is true:
	print "This image has labels? " + str('labelAnnotations' in jsonResponse) + ". Should be True."
	print "This image has landmarks? " + str('landmarkAnnotations' in jsonResponse) + ". Should be False."
	print dots

	### Test: Translate the labels
	innerJSON = classImage.googleToInternalLabelsJSON(jsonResponse)
else:
	pairs = []
	innerJSON = {}
	pairs.append({'community': 0.6809141})
	pairs.append({'memorial': 0.62515974})

	innerJSON['labels'] = json.loads(json.dumps(pairs)) # some JSON

print innerJSON
print dots

### Test: Write labels as Google
classImage.tagPhotoAgnostic(file, innerJSON, curTime, classImage.googleLabelTuple)
### Test: Write labels as Clarifai
classImage.tagPhotoAgnostic(file, innerJSON, curTime, classImage.clarifaiLabelTuple)
### Test: Update Google file history
classImage.updateFileHistory(file, curTime, classImage.googleLabelTuple)
### Test: Update Clarifai file history
classImage.updateFileHistory(file, curTime, classImage.clarifaiLabelTuple)

print dots
readInfo(file)

print dots
googNeed = classImage.decideIfNeedToDo(file, classImage.googleLabelTuple, conn, curTime)
clarNeed = classImage.decideIfNeedToDo(file, classImage.clarifaiLabelTuple, conn, curTime)

print "Need to do Google: " + str(googNeed) + ". Should be False."
print "Need to do Clarif: " + str(clarNeed) + ". Should be False."

### Test: Remove the previous tags from the image one at a time. 
print dots
classImage.removePreviousTags(file, classImage.googleLabelTuple)
readInfo(file)
print dots
classImage.tagPhotoAgnostic(file, innerJSON, curTime, classImage.googleLabelTuple)
classImage.removePreviousTags(file, classImage.clarifaiLabelTuple)
readInfo(file)
print dots

classImage.tagPhotoAgnostic(file, innerJSON, curTime, classImage.clarifaiLabelTuple)
curTime = "1992-10-37 83:02:68"
classImage.updateFileHistory(file, curTime, classImage.clarifaiLabelTuple)
readInfo(file)
print dots
curTime = "1692-77-38 90:37:03"
classImage.updateFileHistory(file, curTime, classImage.googleLabelTuple)
readInfo(file)
print dots
# metadata = pyexiv2.ImageMetadata(file)
# metadata.read()
# metadataFields = metadata.exif_keys

# imHistoryKey = 'Exif.Image.ImageHistory'

# if imHistoryKey in metadataFields:
# 	imHistory = metadata[imHistoryKey].raw_value
# else:
# 	imHistory = ""

# print imHistory 

# regexString = "\s?" + classImage.googleLabelTuple[2] + "\d+-\d+-\d+ \d+:\d+:\d+" + ", orientation is \d."
# print regexString
# historyMatch = re.search(r"" + regexString + "" , imHistory)
# if (historyMatch):
# 	print "is a match"

# removeString = "\s+" + classImage.googleLabelTuple[2] + "" + ", orientation is \d."
# intermediate = re.sub(r"" +  removeString + "" , "", existingTags)
