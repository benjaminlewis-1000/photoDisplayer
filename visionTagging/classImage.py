#! /usr/bin/python

import io
import os
from PIL import Image, ImageFilter
import base64
import cStringIO
import StringIO

from base64 import b64encode
from os import makedirs
from os.path import join, basename
from sys import argv
import json
import requests


ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
# from google.cloud import vision

# from oauth2client.service_account import ServiceAccountCredentials
# from oauth2client.client import flow_from_clientsecrets

# cred = ServiceAccountCredentials.from_json_keyfile_name('Tag Photos-c306bf13c5ab.json.key')

# print 'got creds'
# vision_client = vision.Client()

# testImage = 'C:\\Users\\Benjamin\\Dropbox\\Perl Code\\photoDisplayer\\base\\dirA\\eif.jpg'
testImage = 'C:\\Users\\Benjamin\\Dropbox\\Perl Code\\photoDisplayer\\base\\dirA\\DSC_0648.JPG'



# Recommended size: 640x480 for label detection. I may double that...
desWidth = 1280.0
desHeight = 960.0

# Open the image and get its width and height
# im1 = Image.open(testImage)
# width, height = im1.size

# # Rescale the image if necessary to 2x by 2x the recommended API resolution
# scale = min(width/desWidth, height/desHeight)
# if scale > 0.5:
# 	im1 = im1.resize( (int(width/scale), int(height/scale ) ), Image.ANTIALIAS )
# im1 = im1.resize( (35, 550), Image.ANTIALIAS )

# im1.show()
# Write the resized image to a memory file
# buffer = io.BytesIO()  
# im1.save(buffer, format="JPEG")
# buffer.seek(0)  # Reset the buffer, very important


# imageContent = buffer.read()
# print imageContent[:110] 

# buffer.seek(0)

# image = vision_client.image(content=imageContent)

# labels = image.detect_labels()
# print('Labels:')

# for label in labels:
    # print(label.description)
# print cont[:10] 
# print len(cont)

# buffer.seek(0)
# i2 = Image.open(buffer)
# i2.show()
# buffer.close()  # Close the file in memory; we're done with it. 


# f = open(testImage, 'rb')
# ctxt = b64encode(f.read()).decode()

with io.open(testImage, 'rb') as image_file:
    content = image_file.read()
    print content[:110]
    print len(content)

def make_image_data(image_filenames):
	"""
	image_filenames is a list of filename strings
	Returns a list of dicts formatted as the Vision API
	    needs them to be
	"""
	img_requests = []
	# for imgname in image_filenames:
	print image_filenames

	im1 = Image.open(image_filenames)
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

def request_ocr(api_key, image_filenames):
    response = requests.post(ENDPOINT_URL,
                             data=make_image_data(image_filenames),
                             params={'key': api_key},
                             headers={'Content-Type': 'application/json'})
    return response

api_file = open('googAPIkey.key', 'r')
api_key = api_file.read()
api_file.close()
# api_key = 'AIzaSyAPEPwPBktgLdNT3eHn8wHfaeoiYOT6gRU'
response = request_ocr(api_key, testImage)

for idx, resp in enumerate(response.json()['responses']):
	val = json.loads(json.dumps(resp))
	for i in range(len(val['labelAnnotations'])):
		jsonTag = val['labelAnnotations'][i]

	# for i in range(len(val['landmarkAnnotations'])):
	# 	jsonTag = val['landmarkAnnotations'][i]

print val['labelAnnotations']