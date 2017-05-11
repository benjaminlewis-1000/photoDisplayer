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
# import yaml
import re
from time import sleep
import xmltodict

from clarifai.rest import ClarifaiApp

ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
reload(sys)  # Reload does the trick so we can set default encoding!!!
sys.setdefaultencoding('UTF8')  ### Let us do more than ASCII

# Recommended size: 640x480 for label detection. I double that.
desWidth = 1280.0
desHeight = 960.0

with open('../config/params.xml') as stream:
	try:
		params = xmltodict.parse(stream.read())
	except Exception as exc:
		print(exc)
		exit(1)

googSourceType = 'Goog'
googLabelPrefix = params['params']['visionTaggingParams']['googleTagging']['googVisionLabelPrefix']
googHistoryPrefix = params['params']['visionTaggingParams']['googleTagging']['googImageHistoryPrefix']

googleLabelTuple = (googSourceType, googLabelPrefix, googHistoryPrefix)

clarifaiSourceType = 'Clarifai'
clarifaiLabelPrefix = params['params']['visionTaggingParams']['clarifaiTagging']['clarifaiVisionLabelPrefix']
clarifaiHistoryPrefix = params['params']['visionTaggingParams']['clarifaiTagging']['clarifaiImageHistoryPrefix']

clarifaiLabelTuple = (clarifaiSourceType, clarifaiLabelPrefix, clarifaiHistoryPrefix)


def removePreviousTags(filename, apiLabelTuple, metadata, databasePointer):

	metadataFields = metadata.exif_keys

	userCommentTagKey = 'Exif.Photo.UserComment'
	if userCommentTagKey in metadataFields:
		existingTags = metadata[userCommentTagKey].raw_value
	else:
		return

	print "Existing tags are " + existingTags

	invalidMatch = re.search(r'UUUUU', existingTags)
	if (invalidMatch):
		print "The current tags are not good! Erasing...\n"
		existingTags = ""
	        metadata[userCommentTagKey] = ""
		metadata["Exif.Image.ImageHistory"] = ""
        	metadata.write()

		c = databasePointer.cursor()
		delQuery = '''DELETE FROM visionData WHERE filename = ?'''
		c.execute(delQuery, (filename,) )
		databasePointer.commit()

        	return


	removeString = "\s+" + apiLabelTuple[1] + "[A-Za-z\s]+_[\d\.]+,?"
	intermediate = re.sub(r"" +  removeString + "" , "", existingTags)

	removeString = "^" + apiLabelTuple[1] + "[A-Za-z\s]+_[\d\.]+,?"
	int2 = re.sub(r"" +  removeString + "" , "", intermediate)

	final = re.sub(r'\s+', " ", int2)
	final2 = re.sub(r'^\s', "", final)
	final3 = re.sub(r"charset=\".*\"\s?,?\s?", "", final2)
	final4 = re.sub(r"II", "", final3)

	print final4

	metadata[userCommentTagKey] = final4
	metadata.write()

	return

def logInDatabase(filename, labelTuple, currentTime, databaseConn):
	isPortrait = checkIfIsPortrait(filename)

	insertionQuery = '''INSERT INTO visionData (filename, lastCheckedDate, readAsPortrait, machineVisionSource) VALUES (?, ?, ?, ?)'''
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

def make_image_data_google(image_filenames, type):
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
	try:
		if scale > 0.5:
			im1 = im1.resize( (int(width/scale), int(height/scale ) ), Image.ANTIALIAS )
	except IOError as ioe:
		print "IO Error in google classify: " + str(ioe)
		logfile = open('logErrata.out', 'a')
		print >>logfile, "File " + image_filenames + " was not able to open for classification in Google."
		logfile.close()
		return -1


	buffer = io.BytesIO()  
	im1.save(buffer, format="JPEG")
	buffer.seek(0)  # Reset the buffer, very important

	# Encode in base64
	ctxt = b64encode(buffer.read()).decode()
        print len(ctxt)

	if type == 'label':

		img_requests.append({
			'image': {'content': ctxt},
			'features': [{
					'type': 'LABEL_DETECTION' # Or LANDMARK_DETECTION
				}
			]
		})
	else:

		img_requests.append({
			'image': {'content': ctxt},
			'features': [{
					'type': 'LANDMARK_DETECTION' # Or LANDMARK_DETECTION
				}
			]
		})

	# return img_requests
	return json.dumps({"requests": img_requests }).encode()

def request_labels_and_landmarks_google(api_key, image_filenames, request_type):
	""" POST a request to the Google Vision API servers and return 
	the JSON response.	"""
	b64data = make_image_data_google(image_filenames, request_type)
	if b64data == -1:
		return -1
	response = requests.post(ENDPOINT_URL,
	                         data=b64data,
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

def tagPhotoAgnostic(filename, jsonInput, apiLabelTuple, metadata):
	## Function to tag a photo with labels from the method-agnostic JSON.
	## Assumes that the jsonInput is not empty. 

	assert jsonInput != ""
	assert filename != ""

	metadataFields = metadata.exif_keys

	userCommentTagKey = 'Exif.Photo.UserComment'

	## Check if there are comments and set them to a string we will add
	## to; otherwise, set as empty string. 

	if userCommentTagKey in metadataFields:
		existingTags = metadata[userCommentTagKey].raw_value
		if existingTags is not "":
			existingTags += ", "
	else:
		existingTags = ""

	labels = jsonInput['labels']

	for i in range(len(labels)):
		tag = labels[i].keys()[0]
		score = labels[i][tag]
		builtString = apiLabelTuple[1] + str(tag) + "_" + str(score) + ", "
		existingTags += builtString

	metadata[userCommentTagKey] = str(existingTags[:-2])  #Get rid of the last space and comma


	metadata.modified = True
	## Check if the file is locked ### 
	isUnlocked = os.access(filename, os.W_OK)
	while not isUnlocked:
		sleep(0.1)
		isUnlocked = os.access(filename, os.W_OK)
	try:
		metadata.write()
	except Exception as e:
		print "Exception in writing metdata: Not written. Method tagPhoto"
		print "More info: " + str(e)



def decideIfNeedToDo(filename, sourceTuple, databasePointer, currentTime, metadata):

	""" Check the database to see if we have already processed this file by tagging it with the given API, at the given orientation.
	If so, we can pass. If it's not in the database, we check the image history field, where said information is available.
	If it has been done, we enter it in the database. Only if we have no record of it being processed in the image history
	or in our database will we say that it has NOT been processed an return a FALSE value.
	"""
	assert len(filename) > 0
	assert len(currentTime) > 0
	sourceType = sourceTuple[0]


	c = databasePointer.cursor()

	### Step 1: check if it's in the database. 
	findQuery = '''SELECT lastCheckedDate, readAsPortrait, machineVisionSource, filename FROM visionData WHERE filename = ? AND machineVisionSource = ?'''
	c.execute(findQuery, (filename, sourceType) )
	oneAns = c.fetchone()

	# Check the current orientation
	isPortrait = checkIfIsPortrait(filename)

	if oneAns == None:  # It's not in the database... 
		### It's not in the database. We need to decide if it does need to be done.
		if not 'Exif.Image.ImageHistory' in metadata:
			# print "No image history, not in database"
			return True  ### If there is no image history, we need to do it.
		else:
			imageHistory = metadata['Exif.Image.ImageHistory'].raw_value

		### Parse the image history to see if it's been done for this tuple. 
		regexString = "(" + str(sourceTuple[2]) + ")" + "(\d+-\d+-\d+ \d+:\d+:\d+)," + " orientation is (\d)."
		# print regexString

		historyMatch = re.search(r"" + regexString + "" , imageHistory)

		if (historyMatch):
			### Extract the data from the history
			sourceString = historyMatch.group(1)
			checkedDate = historyMatch.group(2)
			wasReadPortrait = historyMatch.group(3)

			### Add to the database
			addUntrackedQuery = '''INSERT INTO visionData (filename, lastCheckedDate, readAsPortrait, machineVisionSource, validated) VALUES(?, ?, ?, ?, 0)'''
			insertValues = (filename, currentTime, isPortrait, sourceType)
			c.execute(addUntrackedQuery, insertValues)
			# But don't return quite yet - we need to check if it's been updated yet. 
		else:
			# No history for that method and not in database - needs to be done. 
			# print "No image history for this method, not in database"
			return True

	if 'Exif.Photo.UserComment' in metadata:
		### Sometimes something gets really funky, and we get a bunch of crazy 
		### characters (like a ton of 'u's) in the tags section. It's probably 
		### an error of mine, but it's infrequent, so that's OK. 
		tagFields =  str(metadata['Exif.Photo.UserComment'].raw_value)

		commentMatch = re.search(r'UUUUU', tagFields)
		if (commentMatch):
			print "It's gone wrong last time we wrote file " + filename
			metadata['Exif.Image.ImageHistory'] = ""
			metadata['Exif.Photo.UserComment'] = ""
	
			metadata.modified = True
			isUnlocked = os.access(filename, os.W_OK)
			while not isUnlocked:
				sleep(0.1)
				isUnlocked = os.access(filename, os.W_OK)
			try:
				metadata.write()
			except Exception as e:
				print "Exception in writing metdata: Not written. Method decideIfNeedToDo."
				print str(e)
			return True  ### We need to do it. 
		else:
			validatedQuery = "UPDATE visionData SET validated= 1 WHERE filename = ?"
			c.execute(validatedQuery, (filename,))
			databasePointer.commit()


	if oneAns != None and len(oneAns) > 0:
		checkedDate = oneAns[0]
		wasReadPortrait = oneAns[1]
		source = oneAns[2]

	hasRotated = (int(wasReadPortrait) != int(isPortrait))
	if (hasRotated):  # Delete all previous records, so we don't see this again
		delQuery = '''DELETE FROM visionData WHERE filename = ?'''
		c.execute(delQuery, (filename,))
	return hasRotated ## If it's rotated, we should redo it. 

def googleToInternalLabelsJSON(jsonResponse):
	## Translate from the JSON that google returns to an internal, method-agnostic
	## JSON that I use internally. 
	if ('labelAnnotations' in jsonResponse):
		labels = jsonResponse['labelAnnotations']
		labelDict = {}
		pairs = []
		for i in range(len(labels)):
			jsonTag = labels[i]
			labelType = jsonTag['description']
			score = jsonTag['score']
			pairs.append({labelType: score})

		labelDict['labels'] = json.loads(json.dumps(pairs)) # some JSON

		return labelDict
	else:
		return -1

def googleToLandmarksJSON(jsonResponse):
	if ('landmarkAnnotations' in jsonResponse):
		pass
	else:
		return -1

def checkGoogleOddity(jsonResponse):
	# Definition of an oddity: ONLY a landmark (no labels) or no response at all. Logging for my curiosity.
	if ('labelAnnotations' in jsonResponse or 'landmarkAnnotations' in jsonResponse):
		if 'labelAnnotations' not in jsonResponse:
			return True  # Only landmarks
		else:
			return False
	else:
		# No response at all
		return True

def updateFileHistory(filename, currentTime, apiLabelTuple, metadata):

	metadataFields = metadata.exif_keys

	imHistoryKey = 'Exif.Image.ImageHistory'

	if imHistoryKey in metadataFields:
		imHistory = metadata[imHistoryKey].raw_value
	else:
		imHistory = ""

	## Check if we've already recorded this method in history. If so, we are just replacing the date and orientation.
	regexString = "\s?" + apiLabelTuple[2] + "\d+-\d+-\d+ \d+:\d+:\d+" + ", orientation is \d. "
	historyMatch = re.search(r"" + regexString + "" , imHistory)
	if (historyMatch):
		replaceRegex = "\s?" + apiLabelTuple[2] + "\d+-\d+-\d+ \d+:\d+:\d+" + ", orientation is \d. "
		newData = " " + apiLabelTuple[2] + currentTime + ", orientation is " + str(checkIfIsPortrait(filename)) + ". "
		intermediate = re.sub(r"" +  replaceRegex + "" , newData, imHistory)
		metadata[imHistoryKey] = unicode(intermediate, "utf-8")
		metadata.write()
		return

	else: ### There was no history match; append to the file history. 
		imHistory += apiLabelTuple[2] + currentTime + ", orientation is " + str(checkIfIsPortrait(filename)) + ". "
		metadata[imHistoryKey] = imHistory
		
		metadata.modified = True
		isUnlocked = os.access(filename, os.W_OK)
		while not isUnlocked:
			sleep(0.1)
			isUnlocked = os.access(filename, os.W_OK)
		try:
			metadata.write()
		except Exception as e:
			print metadata
			print "Exception in writing metdata: File changed. API is " + apiLabelTuple[2]
			print "More details: " + str(e)

def classifyImageWithGoogleAPI(api_key, filename, databaseConn, currentTime, knownWords):

	metadata = pyexiv2.ImageMetadata(filename)
	metadata.read()

	### Check if the file is locked ### 
	isUnlocked = os.access(filename, os.W_OK)
	if (not isUnlocked):
		print "File " + filename + " is locked. Skipping."
		return 0

	if decideIfNeedToDo(filename, googleLabelTuple, databaseConn, currentTime, metadata):

		print "Classifying image: " + filename
		# Remove any tags that may be floating from Google. 
		removePreviousTags(filename, googleLabelTuple, metadata, databaseConn)
		# Request the response from the API
		response = request_labels_and_landmarks_google(api_key, filename, 'label')
		if response == -1:
			print "Unable to finish Google classify."
			return 0
		# Get the appropriate response.
		jsonLabelResponse = json.loads(json.dumps(response.json()['responses']))[0]

		# File log of the JSON response, just for kicks. 
		outfile = open('out.out', 'w')
		print >>outfile, json.dumps(response.json()['responses'])
		outfile.close()

		# Translate to our internal, platform-agnostic label type.
		innerJSONlabels = googleToInternalLabelsJSON(jsonLabelResponse)
        
		if innerJSONlabels != -1:
			tagPhotoAgnostic(filename, innerJSONlabels, googleLabelTuple, metadata)
			# Go ahead and classify it. LabelAnnotations is in jsonResponse
			# This method should only write the tags
			# tagPhotoFromGoogleJSON(filename, jsonLabelResponse, currentTime, googleLabelTuple)
			pass
		else:
			# We were unable to find any labels for the image. 
			pass

		## Get the different labels that were in the response
		wordList = []
		# print jsonLabelResponse
		if ('labelAnnotations' in jsonLabelResponse):
			match = re.search(r"{u'labelAnnotations': (\[.*?\])", str(jsonLabelResponse))
			# print match
			# print match.group(1)
			if match:
				notations = match.group(1)
				keywords = re.finditer(r"u'description': u'(.*?)'", notations)
				for i in keywords:
					wordList.append(i.group(1))

			# knownWords = ['landmark', 'tourism', 'monument', 'mountain', 'landform', 'tower', 'mountainous landforms', 'vacation', 'place of worship', 'geographical feature', 'building', 'people', 'tours', 'city', 'vehicle', 'temple', 'adventure', 'ancient history', 'human settlement', 'rock', 'body of water', 'architecture', 'town', 'structure', 'memorial', 'water', 'night', 'tree', 'sea', 'historic site', 'art', 'lake', 'arch', 'geological phenomenon', 'natural environment', 'sports', 'wall', 'coast', 'water feature', 'ancient rome', 'community', 'plaza', 'text', 'walking', 'waterfall', 'palace', 'estate', 'mountain range', 'skyline', 'photograph', 'atmosphere of earth', 'garden', 'evening', 'wilderness', 'aerial photography', 'travel', 'loch', 'wadi', 'horizon', 'shore', 'statue', 'blue', 'tower block', 'property', 'reflection', 'metropolitan area', 'interior design', 'image', 'highland', 'skyscraper', 'church', 'crowd', 'shape', 'light', 'lighting', 'screenshot', 'basilica', 'sculpture', 'park', 'boat', 'playground', 'geology', 'child', 'person', 'backyard', 'extreme sport', 'urban area', 'ecosystem', 'atmospheric phenomenon', 'recreation room', 'grass', 'spring', 'nature', 'metropolis', 'flower', 'town square', 'man made object', 'room', 'cliff', 'sport climbing', 'residential area', 'bridge', 'handwriting', 'design', 'watercourse', 'lawn', 'mast', 'newspaper', 'fountain', 'darkness', 'neighbourhood', 'play', 'house', 'color', 'waterway', 'reservoir', 'ocean', 'woody plant', 'desert', 'cityscape', 'ancient roman architecture', 'commemorative plaque', 'document', 'ship', 'cathedral', 'transport', 'fjord', 'line', 'rock climbing', 'stadium', 'watercraft', 'watercraft rowing', 'road', 'games', 'yard', 'formation', 'totem pole', 'plant', 'archaeological site', 'street', 'sign', 'bell tower', 'ruins', 'river', 'arecales', 'badlands', 'hill', 'resort', 'physical fitness', 'sky', 'font', 'drawing', 'writing', 'lane', 'climbing', 'steeple', 'farm', 'brand', 'snow', 'facade', 'fun', 'cloud', 'downtown', 'human positions', 'valley', 'outdoor structure', 'warship', 'fair', 'canyon', 'suspension bridge', 'hiking', 'jumping', 'diagram', 'stage', 'ridge', 'social group', 'mural', 'season', 'track', 'agriculture', 'home', 'naval ship', 'terrain', 'wheel', 'bay', 'day', 'leisure', 'rope bridge', 'electricity', 'destroyer', 'public space', 'advertising', 'green', 'amphitheatre', 'ravine', 'middle ages', 'sunset', 'summit', 'outdoor recreation', 'surfboard', 'rolling stock', 'suburb', 'jungle', 'monastery', 'dusk', 'tourist attraction', 'beach', 'performance', 'control tower', 'stone wall', 'machine', 'endurance', 'cave', 'billiard room', 'controlled access highway', 'stream', 'winter', 'ceremony', 'demonstration', 'automotive exterior', 'landscape', 'pedestrian', 'grass family', 'soil', 'sport venue', 'ferry', 'caving', 'siding', 'human action', 'roof', 'currency', 'aviation', 'cottage', 'walkway', 'passenger ship', 'construction', 'trail', 'performance art', 'altar', 'flight', 'plain', 'fence', 'white', 'canopy walkway', 'grave', 'traffic light', 'panorama', 'festival', 'crew', 'bicycle', 'number', 'cemetery', 'musical instrument', 'mosque', 'industry', 'column', 'restaurant', 'surfing equipment and supplies', 'headstone', 'indoor games and sports', 'sitting', 'marina', 'drums', 'bouldering', 'pit cave', 'dome', 'aeolian landform', 'highway', 'net', 'endurance sports', 'ice', 'sand', 'leg', 'public transport', 'plan', "ch\xe2teau", 'morning', 'signage', 'road trip', 'outdoor play equipment', 'sketch', 'gargoyle', 'floristry', 'drum', 'chapel', 'asphalt', 'dock', 'physical exercise', 'material', 'hill station', 'vendor', 'family', 'circle', 'money', 'black', 'hammock', 'relief', 'swimming pool', 'silver', 'triumphal arch', 'mountaineering', 'yellow' ]

			## Get a boolean to see if there are any shared words between the lists. 
			sharedWords = bool(set(wordList) & set(knownWords) )
			if (sharedWords):
				print "Found a possible landmark phrase: " + str(set(wordList) & set(knownWords) )
				jsonLandmarkResponse = request_labels_and_landmarks_google(api_key, filename, 'landmarks')

				if 'landmarkAnnotations' in jsonLandmarkResponse:
					tagPhotoGoogleGPS(filename, jsonLabelResponse, googleLabelTuple, metadata)
					logfile = open('logLandmarks.out', 'a')
					print >>logfile, filename + " : " + str(jsonLabelResponse)


		## Update the file history and log the file in the database. This should be done 
		## regardless of the file characteristics that were found. 
		updateFileHistory(filename, currentTime, googleLabelTuple, metadata)
		logInDatabase(filename, googleLabelTuple, currentTime, databaseConn)


		if checkGoogleOddity(jsonLabelResponse):			
			logfile = open('logErrata.out', 'a')
			print >>logfile, "File " + filename + " has no labelAnnotations, and may or may not have a landmarkAnnotation." + "\n..." + str(jsonLabelResponse)
			logfile.close()

		return 1

	else:
		# print "Don't need to do this one: " + filename
		return 0

def tagPhotoGoogleGPS(filename, jsonInput, apiLabelTuple, metadata):

	assert jsonInput != ""
	assert filename != ""

	metadataFields = metadata.exif_keys

	userCommentTagKey = 'Exif.Photo.UserComment'

	## Check if there are comments and set them to a string we will add
	## to; otherwise, set as empty string. 
	if userCommentTagKey in metadataFields:
		existingTags = metadata[userCommentTagKey].raw_value
		if existingTags is not "":
			existingTags += ", "
	else:
		existingTags = ""

	place = jsonInput['landmarkAnnotations'][0]  # Just get the top scoring place. 
	print place
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

	isUnlocked = os.access(filename, os.W_OK)
	while not isUnlocked:
		sleep(0.1)
		isUnlocked = os.access(filename, os.W_OK)
	try:
		metadata.write()
	except Exception as e:
		print "Exception in writing metdata: Not written. Method tagWithGPS"
		print "More info: " + str(e)

	if 'description' in place:
		jsonTag = {}
		pairs = []
		pairs.append({place['description']: place['score']})
		jsonTag['labels'] = json.loads(json.dumps(pairs)) # some JSON
		tagPhotoAgnostic(filename, jsonTag, googleLabelTuple, metadata)


def readInfo(filename):
	metadata = pyexiv2.ImageMetadata(filename)
	metadata.read()
	imageHistoryField = 'Exif.Image.ImageHistory'
	commentField = 'Exif.Photo.UserComment'
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

def clarifaiClassify(filename, app_id, app_secret):

	app = ClarifaiApp(app_id, app_secret)
	model = app.models.get("general-v1.3")

	desWidth = 1280.0
	desHeight = 960.0

	im1 = openImageOriented(filename)
	# im1 = Image.open(image_filenames)
	width, height = im1.size

	# Rescale the image if necessary to 2x by 2x the recommended API resolution
	scale = min(width/desWidth, height/desHeight)
	try:
		if scale > 0.5:
			im1 = im1.resize( (int(width/scale), int(height/scale ) ), Image.ANTIALIAS )
	except IOError as ioe:
		print "IO Error in clarifai classify: " + str(ioe)
		logfile = open('logErrata.out', 'a')
		print >>logfile, "File " + filename + " was not able to open for classification in Clarifai."
		logfile.close()
		return -1


	buffer = io.BytesIO()  
	im1.save(buffer, format="JPEG")
	buffer.seek(0)  # Reset the buffer, very important

	# Encode in base64
	ctxt = b64encode(buffer.read()).decode()

	clarifaiJSON = model.predict_by_base64(ctxt)

	tags = clarifaiToInternalLabelsJSON(clarifaiJSON)

	return tags


def classifyImageWithClarifaiAPI(filename, app_id, app_secret, databaseConn, currentTime):

	metadata = pyexiv2.ImageMetadata(filename)
	metadata.read()

	### Check if the file is locked ### 
	isUnlocked = os.access(filename, os.W_OK)
	if (not isUnlocked):
		print "File " + filename + " is locked. Skipping."
		return 0

	if decideIfNeedToDo(filename, clarifaiLabelTuple, databaseConn, currentTime, metadata):

		print "Classifying image: " + filename
		# Remove any tags that may be floating from Google. 
		removePreviousTags(filename, clarifaiLabelTuple, metadata, databaseConn)
		# Request the response from the API. Clarifai returns in the agnostic form already.
		jsonResponse = clarifaiClassify(filename, app_id, app_secret)
		if jsonResponse == -1:
			print "Unable to complete Clarifai classify for this image."
			return 0

		# File log of the JSON response, just for kicks. 
		outfile = open('out.out', 'w')
		print >>outfile, jsonResponse
		outfile.close()

		# Translate to our internal, platform-agnostic label type.
		if jsonResponse != -1:
			tagPhotoAgnostic(filename, jsonResponse, clarifaiLabelTuple, metadata)
			# Go ahead and classify it. LabelAnnotations is in jsonResponse
			# This method should only write the tags
		else:
			# We were unable to find any labels for the image. 
			pass

		## Update the file history and log the file in the database. This should be done 
		## regardless of the file characteristics that were found. 
		updateFileHistory(filename, currentTime, clarifaiLabelTuple, metadata)
		logInDatabase(filename, clarifaiLabelTuple, currentTime, databaseConn)


		# if checkGoogleOddity(jsonResponse):			
		# 	logfile = open('logErrata.out', 'a')
		# 	print >>logfile, "File " + filename + " has no labelAnnotations, and may or may not have a landmarkAnnotation." + "\n..." + jsonResponse
		# 	logfile.close()
		return 1

	else:
		# print "Don't need to do this one: " + filename
		return 0

def clarifaiToInternalLabelsJSON(jsonResponse):
	## Translate from the JSON that google returns to an internal, method-agnostic
	## JSON that I use internally. 

	dataJSON = jsonResponse['outputs'][0]['data']

	if ('concepts' in dataJSON):
		labels = dataJSON['concepts']
		labelDict = {}
		pairs = []
		for i in range(len(labels)):
			jsonTag = labels[i]
			labelType = jsonTag['name']
			score = jsonTag['value']
			pairs.append({labelType: score})

		labelDict['labels'] = json.loads(json.dumps(pairs)) # some JSON

		return labelDict
	else:		
		logfile = open('logErrata.out', 'a')
		print >>logfile, "File " + filename + " has no labelAnnotations in Clarifai."
		logfile.close()
		return -1
