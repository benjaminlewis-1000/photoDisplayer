#! /usr/bin/python

import classImage
import pyexiv2
import sqlite3
import sys

conn = sqlite3.connect("visionDatabase.db")

file = "/mnt/NAS/Photos/Family CDs/Family May 04 - Jul 05/2005-07-10/100_2618.JPG"
file = sys.argv[1]
md = pyexiv2.ImageMetadata(file)
md.read()

api_file = open('clarifaiAPIkey.key', 'r')
app_id = api_file.readline().rstrip("\n\r")
app_secret = api_file.readline()
api_file.close()

classImage.openImageOriented(file)
classImage.decideIfNeedToDo(file, classImage.clarifaiLabelTuple, conn, "2017-04-13 00:00:00", md)

classImage.readInfo(file)

try:
	classImage.classifyImageWithClarifaiAPI(file, app_id, app_secret, conn, "2017-04-13 00:00:00")
except IOError as e:
	print "Head IO Error: " + str(e)
except Exception as e:
	print "Other exception! Oh noes!"
	print str(e)

