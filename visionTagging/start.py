#! /usr/bin/python

import datetime
import os
import pyexiv2 as pe2
import re
import sqlite3
from time import gmtime, strftime


curTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
conn = sqlite3.connect("visionDatabase.db")
conn.text_factory = str  # For UTF-8 compatibility
c = conn.cursor()

dir = 'D:\Pictures\\2016\\Apartment Painting\\'

listAllFiles = []
ext = [".JPG", ".jpg", ".jpeg", ".JPEG"]

for dirpath, dirnames, filenames in os.walk(dir):
	for fname in filenames:
		if fname.endswith(tuple(ext)):
			listAllFiles.append(os.path.join(dirpath, fname))

#####   Tag file routine   #####

picasaTagField = 'Iptc.Application2.Keywords'
imageHistoryField = 'Exif.Image.ImageHistory'
commentField = 'Exif.Photo.UserComment'

def classifyImage():
	pass

def tagFile(file):
	metadata = pe2.ImageMetadata(file)
	metadata.read()
	history = metadata['Exif.Image.ImageHistory'].raw_value
	m = re.search('^Google added: ', tagVal)
	if ~m: 
		pass 
		# We haven't added anything yet. 
		# This is where we go and plead to google to classify our image


tagsOfInterest = ['Exif.Image.ImageDescription', 'Exif.Image.ImageID', 'Exif.Image.SecurityClassification', 'Exif.Image.ImageHistory',   'Exif.Photo.UserComment', 'Iptc.Application2.Caption']  # Application2.Keywords - picasa keywords


testImage = "../base/dirA/marky.jpg"
metadata = pe2.ImageMetadata(testImage)
metadata.read()

print metadata.iptc_keys
# for tag in tagsOfInterest:
# 	if tag in metadata:
# 		print tag + ": " + metadata[tag].raw_value
# 		tagVal = metadata[tag].raw_value
# 		m = re.search('^Google added: ', tagVal)
# 		if m:
# 			print m.group(0)

for t in tagsOfInterest:
	print t
	print  metadata[t].raw_value



# key = 'Exif.Image.ImageHistory'
# metadata[key] = "Google added: " + curTime
# metadata.write()

# key = 'Exif.Photo.UserComment'
# metadata[key] = "This is a comment"
# metadata.write()


#####   List file routine   ####

"""
for file in listAllFiles:
	modTime = datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y-%m-%d %H:%M:%S")

	query = "SELECT lastCheckedDate FROM visionData WHERE fileName = \"" + file + "\""

	lastSeen = ""

	for row in c.execute(query):
	    lastSeen = row[0]

	if lastSeen != "": # We have already tagged this file once using Google Vision API, but we need to check it.
		needsUpdating = modTime > lastSeen
		if needsUpdating:
			tagFile(file)

		#TODO: Need to see if we have 

	else:  # This file has never seen the light of Google Vision API, so we need to tag it regardless. 
		tagFile(file)

"""
