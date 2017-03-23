#! /usr/bin/python

import io
import os
from PIL import Image, ImageFilter
from base64 import b64encode
from sys import argv
import sys
import json
import requests
import pyexiv2
import yaml
import re

ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
reload(sys)  # Reload does the trick so we can set default encoding!!!
sys.setdefaultencoding('UTF8')  ### Let us do more than ASCII

# Recommended size: 640x480 for label detection. I double that.
desWidth = 1280.0
desHeight = 960.0

with open('../config/params.yaml') as stream:
	try:
		yParams = yaml.load(stream)
	except yaml.YAMLError as exc:
		print(exc)

googSourceType = 'Goog'
googLabelPrefix = yParams['googVisionLabelPrefix'] 
googHistoryPrefix = yParams['googImageHistoryPrefix']

googleLabelTuple = (googSourceType, googLabelPrefix, googHistoryPrefix)





def removePreviousTags(filename, apiLabelTuple):
	metadata = pyexiv2.ImageMetadata(filename)
	metadata.read()
	metadataFields = metadata.exif_keys

	userCommentTagKey = 'Exif.Photo.UserComment'
	if userCommentTagKey in metadataFields:
		existingTags = metadata[userCommentTagKey].raw_value
	else:
		return

	print existingTags

	removeString = "\s+" + apiLabelTuple[1] + "[A-Za-z\s]+_[\d\.]+,?"
	intermediate = re.sub(r"" +  removeString + "" , "", existingTags)

	removeString = "^" + apiLabelTuple[1] + "[A-Za-z\s]+_[\d\.]+,?"
	int2 = re.sub(r"" +  removeString + "" , "", intermediate)

	final = re.sub(r'\s+', " ", int2)
	final = re.sub(r'^\s', "", final)

	print "VV is " + final
	# print existingTags



	# metadataFields[userCommentTagKey] = final

	return

def logInDatabase(filename, labelTuple, currentTime, databaseConn):
	isPortrait = checkIfIsPortrait(filename)

	insertionQuery = '''INSERT INTO visionData (fileName, lastCheckedDate, readAsPortrait, machineVisionSource) VALUES (?, ?, ?, ?)'''
	insertionVals = (filename, currentTime, isPortrait, labelTuple[0])
	c = databaseConn.cursor()
	c.execute(insertionQuery, insertionVals)
	databaseConn.commit()

def to_deg(value, type):
        """
		Take a degree GPS position and converts it to the format needed for EXIF data. Taken from GitHub account 
		https://gist.github.com/maxim75/985060#file-set_loc-py-L50
        """
        abs_value = abs(value)
        deg =  int(abs_value)

        if type == "lat":
        	sign = lambda x: ("N", "S")[x < 0]
        	hemisphere = sign(value)
        else:
        	sign = lambda x: ("E", "W")[x < 0]
        	hemisphere = sign(value)

        t1 = (abs_value-deg)*60
        min = int(t1)
        sec = round((t1 - min)* 60, 5)
        return (deg, min, sec, hemisphere)

def openImageOriented(filename):
	""" Open an image and discover its orientation.
	Rotate the image in the container if necessary, then
	return the image.
	"""
	metadata = pyexiv2.ImageMetadata(filename)
	metadata.read()
	try:
		image=Image.open(filename)
		orientation = metadata['Exif.Image.Orientation'].raw_value
		exif=dict(image._getexif().items())

		if orientation == 3:
			image=image.rotate(180, expand=True)
		elif orientation == 6:
			image=image.rotate(270, expand=True)
		elif orientation == 8:
			image=image.rotate(90, expand=True)

		return image

	except (AttributeError, KeyError, IndexError):
	# cases: image don't have getexif
		image=Image.open(filename)
		return image

def make_image_data_google(image_filenames):
	"""
	image_filenames is a list of filename strings
	Returns a list of dicts formatted as the Google Vision API
	    needs them to be
	"""
	img_requests = []

	im1 = openImageOriented(image_filenames)
	# im1 = Image.open(image_filenames)
	width, height = im1.size

	# Rescale the image if necessary to 2x by 2x the recommended API resolution
	scale = min(width/desWidth, height/desHeight)
	if scale > 0.5:
		im1 = im1.resize( (int(width/scale), int(height/scale ) ), Image.ANTIALIAS )

	buffer = io.BytesIO()  
	im1.save(buffer, format="JPEG")
	buffer.seek(0)  # Reset the buffer, very important

	# Encode in base64
	ctxt = b64encode(buffer.read()).decode()

	img_requests.append({
		'image': {'content': ctxt},
		'features': [{
				'type': 'LABEL_DETECTION' # Or LANDMARK_DETECTION
			},{
				'type': 'LANDMARK_DETECTION' # Or LANDMARK_DETECTION
			}
		]
	})
	# return img_requests
	return json.dumps({"requests": img_requests }).encode()

def request_labels_and_landmarks_google(api_key, image_filenames):
	""" POST a request to the Google Vision API servers and return 
	the JSON response.	"""
	response = requests.post(ENDPOINT_URL,
	                         data=make_image_data_google(image_filenames),
	                         params={'key': api_key},
	                         headers={'Content-Type': 'application/json'})
	return response

def checkIfIsPortrait(filename):
	""" Open the filename and get its dimensions. Assign a 1 if it is portrait,
	else a 0 if it is landscape. This should be the only method for determining this in
	this class so that we can keep consistency.
	"""
	im1 = openImageOriented(filename)
	width, height = im1.size
	im1.close()

	if height > width:
		isPortrait = 1
	else:
		isPortrait = 0

	return isPortrait


def tagPhotoFromGoogleJSON(filename, jsonInput, currentTime, apiLabelTuple):

	# print "Input is " +  str(jsonInput)

	metadata = pyexiv2.ImageMetadata(filename)
	metadata.read()
	metadataFields = metadata.exif_keys

	imHistoryKey = 'Exif.Image.ImageHistory'
	userCommentTagKey = 'Exif.Photo.UserComment'

	if imHistoryKey in metadataFields:
		imHistory = metadata[imHistoryKey].raw_value
	else:
		imHistory = ""

	imHistory += apiLabelTuple[2] + currentTime + ", orientation is " + str(checkIfIsPortrait(filename)) + "."
	metadata[imHistoryKey] = imHistory

	if userCommentTagKey in metadataFields:
		existingTags = metadata[userCommentTagKey].raw_value
		if existingTags is not "":
			existingTags += ", "
	else:
		existingTags = ""

	if 'labelAnnotations' in jsonInput:
		for i in range(len(jsonInput['labelAnnotations'])):
			jsonTag = jsonInput['labelAnnotations'][i]
			labelType = jsonTag['description']
			score = jsonTag['score']
			# print str(labelType) + ": " + str(score)
			builtString = apiLabelTuple[1] + str(labelType) + "_" + str(score) + ", "
			existingTags += builtString

	if 'landmarkAnnotations' in jsonInput:
		# for i in len(jsonInput['landmarkAnnotations']):
		# 	place = jsonInput['landmarkAnnotations'][i]
		place = jsonInput['landmarkAnnotations'][0]  # Just get the top scoring place. 
		if 'description' in place:
			description = place['description']
			score = place['score']
			existingTags += apiLabelTuple[1] + str(description) + "_" + str(score) + ", "
		latLong = place['locations'][0]['latLng']
		lat = latLong['latitude']
		lng = latLong['longitude']
		lat_deg = to_deg(lat, 'lat')
		lng_deg = to_deg(lng, 'lng')
		exiv_lat = (pyexiv2.Rational(lat_deg[0]*60+lat_deg[1],60),pyexiv2.Rational(lat_deg[2]*100,6000), pyexiv2.Rational(0, 1))
		exiv_lng = (pyexiv2.Rational(lng_deg[0]*60+lng_deg[1],60),pyexiv2.Rational(lng_deg[2]*100,6000), pyexiv2.Rational(0, 1))
		metadata["Exif.GPSInfo.GPSLatitude"] = exiv_lat
		metadata["Exif.GPSInfo.GPSLatitudeRef"] = lat_deg[3]
		metadata["Exif.GPSInfo.GPSLongitude"] = exiv_lng
		metadata["Exif.GPSInfo.GPSLongitudeRef"] = lng_deg[3]
		metadata["Exif.Image.GPSTag"] = 654
		metadata["Exif.GPSInfo.GPSMapDatum"] = "WGS-84"
		metadata["Exif.GPSInfo.GPSVersionID"] = '2 0 0 0'
		# set_gps_location(metadata, lat, lng)

		# print description + " " + str(lat) + " " + str(lng)

	metadata[userCommentTagKey] = existingTags[:-2]  #Get rid of the last space and comma

	metadata.write()


def decideIfNeedToDo(filename, sourceTuple, databasePointer, currentTime):

	""" Check the database to see if we have already processed this file by tagging it with the given API, at the given orientation.
	If so, we can pass. If it's not in the database, we check the image history field, where said information is available.
	If it has been done, we enter it in the database. Only if we have no record of it being processed in the image history
	or in our database will we say that it has NOT been processed an return a FALSE value.
	"""
	assert len(filename) > 0
	assert len(currentTime) > 0

	sourceType = sourceTuple[0]

	### Step 1: check if it's in the database. 
	c = databasePointer.cursor()
	findQuery = '''SELECT lastCheckedDate, readAsPortrait, machineVisionSource, fileName FROM visionData WHERE fileName = ? AND machineVisionSource = ?'''
	c.execute(findQuery, (filename, sourceType) )

	isPortrait = checkIfIsPortrait(filename)

	oneAns = c.fetchone()
	# print oneAns
	if oneAns == None:
		### It's not in the database. We need to decide if it does need to be done.
		metadata = pyexiv2.ImageMetadata(filename)
		metadata.read()
		if not 'Exif.Image.ImageHistory' in metadata:
			return True  ### If there is no image history, we need to do it.
		imageHistory = metadata['Exif.Image.ImageHistory'].raw_value

		regexString = "([A-Za-z_]+)" + "(\d+-\d+\d+ \d+:\d+:\d+), orientation is (\d)."

		historyMatch = re.search(r"" + regexString + "" , imageHistory)

		if (historyMatch):
			print historyMatch
			sourceString = historyMatch.group(1)
			checkedDate = historyMatch.group(2)
			wasReadPortrait = historyMatch.group(3)

		### Add to the database
			addUntrackedQuery = '''INSERT INTO visionData (fileName, lastCheckedDate, readAsPortrait, machineVisionSource) VALUES(?, ?, ?, ?)'''
			insertValues = (filename, currentTime, isPortrait, sourceType)
			c.execute(addUntrackedQuery, insertValues)
		else:
			return True

	if oneAns != None and len(oneAns) > 0:
		checkedDate = oneAns[0]
		wasReadPortrait = oneAns[1]
		source = oneAns[2]

	hasRotated = (int(wasReadPortrait) != int(isPortrait))
	if (hasRotated):  # Delete all previous records, so we don't see this again
		delQuery = '''DELETE FROM visionData WHERE fileName = ?'''
		c.execute(delQuery, (filename,))
	return hasRotated ## If it's rotated, we should redo it. 



def classifyImageWithGoogleAPI(api_key, filename, databaseConn, currentTime):

	### Check if the file is locked ### 
	isUnlocked = os.access(filename, os.W_OK)
	if (not isUnlocked):
		print "File " + filename + " is locked. Skipping."
		return

	if decideIfNeedToDo(filename, googleLabelTuple, databaseConn, currentTime):
		print "Classifying image: " + filename
		removePreviousTags(filename, googleLabelTuple)
		response = request_labels_and_landmarks_google(api_key, filename)
		jsonResponse = json.loads(json.dumps(response.json()['responses']))[0]

		print jsonResponse

		outfile = open('out.out', 'w')
		print >>outfile, json.dumps(response.json()['responses'])
		outfile.close()
		if ('labelAnnotations' in jsonResponse or 'landmarkAnnotations' in jsonResponse):
			if 'labelAnnotations' in jsonResponse: # I've seen it happen - a landmark with no labels.
				print jsonResponse['labelAnnotations']
			else:
				logfile = open('logErrata.out', 'a')
				print >>logfile, "File " + filename + " has no labelAnnotations, but does have a landmarkAnnotation."
				logfile.close()
			tagPhotoFromGoogleJSON(filename, jsonResponse, currentTime, googleLabelTuple)

		logInDatabase(filename, googleLabelTuple, currentTime, databaseConn)
	else:
		print "Don't need to do this one: " + filename
		# pass
