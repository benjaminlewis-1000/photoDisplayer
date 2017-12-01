#! /usr/bin/python

import pyexiv2
import os
import re

import SimpleHTTPServer
import SocketServer
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import xmlrpclib
import socket
import xmltodict
socket.setdefaulttimeout(10)        #set the timeout to 10 second

proxy = xmlrpclib.ServerProxy("http://127.0.0.1:8040/RPC2")

project_path = os.path.abspath(os.path.join(__file__,"../.."))
script_path  = os.path.abspath(os.path.join(__file__,".."))

with open(script_path + '/config/params.xml') as stream:
    try:
        params = xmltodict.parse(stream.read())
    except Exception as exc:
        print(exc)
        exit(1)

# val = proxy.geoLookup(40.258055556, -111.6375)
# print val.encode('utf-8')

# name = re.sub(r'((?<!\')[a-zA-Z\'\s,])', lambda pat: pat.group(1).lower(), name);
# name = re.sub(r'([A-Za-z\']+)', lambda pat: pat.group(1).capitalize(), name)
# print name

# rootDirectory = "N:\Photos\Family Pictures\\2016\October 2016 A\\"
# for dirpath, dirnames, filenames in os.walk(rootDirectory):
#     for fname in filenames:
#         if fname.endswith(tuple([".JPG", ".jpg", ".jpeg", ".JPEG"])):
#             filename = os.path.join(dirpath, fname)
#             filename = "N:\\Photos\\Family CDs\\More Pictures\\7-30-05\\DSCN1680.JPG"
#             print filename
#             metadata = pyexiv2.ImageMetadata(filename)
#             metadata.read()

#             autoTags = metadata['Exif.Photo.UserComment'].raw_value
#             tagSplit = autoTags.split(', ')
#             tts = []
#             # print tagSplit
#             for tag in tagSplit:
#                 tag = re.sub(r'' + params['params']['visionTaggingParams']['googleTagging']['googVisionLabelPrefix'] , '', tag)
#                 tag = re.sub(r'' + params['params']['visionTaggingParams']['clarifaiTagging']['clarifaiVisionLabelPrefix'] , '', tag)
#                 if re.search(r'_', tag):
#                     (name, val) = tag.split('_')
#                     # print name + " " + val

#                     tagPair = (name, val)
#                     tts.append(tagPair)

#             print tts

    # for com in enumerate(commentSplit):
    #     com = re.sub(r'googVision_', '', com)
    # print commentSplit

filename = "N:\\Photos\\Family CDs\\More Pictures\\7-30-05\\DSCN1680.JPG"
filename = "D:\\Pictures\\Family Pictures\\2008\\2008-05-29\\100_4140.JPG"
filename = "D:\Pictures\Masters 2014-15\\nick_and_charlotte_texts (2).jpeg"
filename = "N:\\Photos\\2016\\Wedding Time\\Honeymoon San Fran\\DSC_8715.JPG"
metadata = pyexiv2.ImageMetadata(filename)
metadata.read()
metadataFields = metadata.iptc_keys + metadata.xmp_keys + metadata.exif_keys 
# print metadataFields
tmpFile = open(script_path + '/blah.txt', 'w')
print script_path + '/blah.txt'
print >>tmpFile, metadata
# print metadata['Exif.Image.ImageWidth'].raw_value
for i in range(len(metadataFields)):

    if re.search(r'2016', str(metadata[metadataFields[i]].raw_value), re.IGNORECASE):
        print str(metadataFields[i]) + ": " + str(metadata[metadataFields[i]].raw_value)


    if 'Iptc.Application2.DateCreated' in metadata and 'Iptc.Application2.TimeCreated' in metadata:
        date = metadata['Iptc.Application2.DateCreated'].raw_value[0]
        time = metadata['Iptc.Application2.TimeCreated'].raw_value[0]
        dateOrig = str(date) + " " + str(time)
        print dateOrig  

from PIL import Image
def get_date_taken(path):
    return Image.open(path)._getexif()[36867]

print get_date_taken(filename)


            # metadataFields = metadata.xmp_keys
            # # print metadata            nameList = []
            # for i in range(len(metadataFields)):
            #     if re.search(r'Name', metadataFields[i], re.IGNORECASE):
            #         # print metadataFields[i] + ": " + metadata[metadataFields[i]].raw_value
            #         nameSplit = metadata[metadataFields[i]].raw_value
            #         nameSplit = nameSplit.split(": ")
            #         # print nameSplit
            #         name = nameSplit[0]
            #         if not re.search(r'^\.', name):
            #             name = ' '.join([s[0].upper() + s[1:] for s in name.split(' ')])
            #             nameList.append(name)
            # # print type(metadataFields)
            # r = re.compile(".*Region.*")
            # newList = filter(r.match, metadataFields)
            # print nameList
            # # for i in range(len(newList)):
                # print newList[i] + " " + metadata[newList[i]].raw_value


            # if 'Exif.GPSInfo.GPSLatitudeRef' in metadata:
            #     northSouth = metadata['Exif.GPSInfo.GPSLatitudeRef'].raw_value
            #     eastWest = metadata['Exif.GPSInfo.GPSLongitudeRef'].raw_value
            #     lat = str(metadata['Exif.GPSInfo.GPSLatitude'].raw_value)
            #     lon = str(metadata['Exif.GPSInfo.GPSLongitude'].raw_value)
            #     latSplit = lat.split(" ")
            #     lonSplit = lon.split(" ")
            #     assert len(latSplit) == 3
            #     assert len(lonSplit) == 3
            #     latDec = 1.0 * eval(latSplit[0]) + 1.0/60 * eval(latSplit[1]) + 1.0/3600 * eval(latSplit[2])
            #     lonDec = 1.0 * eval(lonSplit[0]) + 1.0/60 * eval(lonSplit[1]) + 1.0/3600 * eval(lonSplit[2])
            #     # print "{}, {}".format(latDec, lonDec)
            # print newList

