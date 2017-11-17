#! /usr/bin/python

import pyexiv2
import os
import re
import sys
from datetime import datetime
from dateutil import parser
import json
import xmltodict
import xmlrpclib
from time import sleep

import socket
socket.setdefaulttimeout(4)        #set the timeout to 10 second

project_path = os.path.abspath(os.path.join(__file__,"../.."))
script_path  = os.path.abspath(os.path.join(__file__,".."))

with open(project_path + '/config/params.xml') as stream:
    try:
        params = xmltodict.parse(stream.read())
    except Exception as exc:
        print(exc)
        exit(1)

# desiredField = "Exif.Photo.DateTimeOriginal"

'''
Fields to get:
= Names (and areas?)
= File creation date
na Modification date
na FileSize
na Image Width
na Image Height
= GPS Lat
= GPS Long
- Keywords (See classImage)
= Time zone (where applicable)
'''

def getExifData(filename, doGeocode):

    if filename.endswith(tuple([".JPG", ".jpg", ".jpeg", ".JPEG"])):
        # filename = os.path.join(dirpath, fname)
        # print filename
        metadata = pyexiv2.ImageMetadata(filename)
        try:
            metadata.read()
        except IOError as ioe:
            print str(ioe)
            exit(1)
        dateOK = True
        # Preferred fields: 'Exif.Photo.DateTimeOriginal' or 'Exif.Photo.DateTimeDigitized'
        if ('Exif.Photo.DateTimeOriginal' not in metadata) and ('Exif.Photo.DateTimeDigitized' not in metadata):
            # print "Time not found!"
            if 'Iptc.Application2.DateCreated' in metadata and 'Iptc.Application2.TimeCreated' in metadata:
                # Backup case - there is no dateTimeOriginal field, but we do have application2 fields to that effect.
                date = metadata['Iptc.Application2.DateCreated'].raw_value[0]
                time = metadata['Iptc.Application2.TimeCreated'].raw_value[0]
                dateTime = [date, time]
                dateIso = str(date) + " " + str(time)
                logfile = open(script_path + '/logNoDates.out', 'a')
                print >>logfile, "Question the time for: " + filename + " : " + dateIso
                logfile.close()
            else:
                dateOK = False
        else:
            if 'Exif.Photo.DateTimeOriginal' in metadata: # Preferred, I think? 
                dateOrig = metadata["Exif.Photo.DateTimeOriginal"].raw_value
                if not re.search(r'[0-9]', dateOrig) or re.search(r'0000:00:00 00:00:00', dateOrig):
                    if 'Exif.Photo.DateTimeDigitized' in metadata:
                        dateOrig = metadata['Exif.Photo.DateTimeDigitized'].raw_value
                    else:
                        dateOK = False
                    # Don't need similar in the else clause below, because in that clause we know DTO isn't there.
            else:
                dateOrig = metadata['Exif.Photo.DateTimeDigitized'].raw_value
            dateTime = dateOrig.split(" ")
            # print dateOrig
            # Error case - there is a valid field, but it contains no numbers. 
            if not re.search(r'[0-9]', dateOrig) or re.search(r'0000:00:00 00:00:00', dateOrig):
                dateOK = False
            dateIso = dateTime[0].replace(":", "-") + " " +  dateTime[1]
        if not dateOK:
            dateTime = ["1969-01-01", "00:00:01"]
            dateIso = "1969-01-01 00:00:01"
            logfile = open(script_path + '/logNoDates.out', 'a')
            try:
                utf_filename = filename.encode('utf-8')
            except UnicodeDecodeError as ude:
                utf_filename = filename
                logfile = open(script_path + '/unicodeTagErrors.out', 'a')
                print >>logfile, "Unicode Date Error in this file: " + str(utf_filename)
            print >>logfile, "No date/time for: " + utf_filename
            logfile.close()
            return -1

        assert len(dateTime) == 2  # Date and time
        assert len(dateTime[0]) == 10 # Date is of format YYYY:MM:DD
        assert len(str(dateTime[1])) == 8 or len(str(dateTime[1])) == 14

        # assert dateOK
        dt = parser.parse(dateIso)
        # print dt
        jData = {}
        jData['ISO8601'] = dateIso
        jData['year'] = dt.year
        jData['month'] = dt.month
        jData['day'] = dt.day
        jData['hour'] = dt.hour
        jData['min'] = dt.minute
        jData['sec'] = dt.second

        if 'Exif.NikonWt.Timezone' in metadata:
            jData['TimeZone'] = metadata['Exif.NikonWt.Timezone'].raw_value
        else:
            jData['TimeZone'] = '0'

        if ('Exif.GPSInfo.GPSLatitudeRef' in metadata):
            northSouth = metadata['Exif.GPSInfo.GPSLatitudeRef'].raw_value
            eastWest = metadata['Exif.GPSInfo.GPSLongitudeRef'].raw_value
            lat = str(metadata['Exif.GPSInfo.GPSLatitude'].raw_value)
            lon = str(metadata['Exif.GPSInfo.GPSLongitude'].raw_value)
            latSplit = lat.split(" ")
            lonSplit = lon.split(" ")
            assert len(latSplit) == 3
            assert len(lonSplit) == 3
            latDec = 1.0 * eval(latSplit[0] + '.0') + 1.0/60.0 * eval(latSplit[1] + '.0') + 1.0/3600.0 * eval(latSplit[2] + '.0')
            lonDec = 1.0 * eval(lonSplit[0] + '.0') + 1.0/60.0 * eval(lonSplit[1] + '.0') + 1.0/3600.0 * eval(lonSplit[2] + '.0')

            if (northSouth != "N"):
                latDec *= -1.0
            if (eastWest != "E"):
                lonDec *= -1.0

            jData['latitude'] = latDec
            jData['longitude'] = lonDec

            # print "{} {} / {} {}".format(lat, lon, latDec, lonDec)


            if doGeocode:
                # passed = False
                # while not passed:
                proxy = xmlrpclib.ServerProxy("http://127.0.0.1:" + params['params']['serverParams']['geoServerPort'] + "/RPC2")
                try:
                    val = proxy.geoLookup(latDec, lonDec)
                    if val == -1:
                        return -1
                    else:
                        try:
                            val = json.loads(val.encode('utf-8'))
                        except Exception as e :
                            print "No JSON Object..."
                    passed = True
                except Exception as e :
                    return str(e)



                jData['house_number'] = val['house_number']
                jData['road'] = val['road']
                jData['city'] = val['city']
                jData['state'] = val['state']
                jData['postcode'] = val['postcode']
                jData['country'] = val['country']
                    # $jsonData->{'postcode'} =~ m/(\d+)/g;
                    # my $postcode = $1;
            else:
                jData['latitude'] = "-"
                jData['longitude'] = "-"
                jData['house_number'] = "-"
                jData['road'] = "-"
                jData['city'] = "-"
                jData['state'] = "-"
                jData['postcode'] = "-"
                jData['country'] = "-"
        else:
            jData['latitude'] = "-"
            jData['longitude'] = "-"
            jData['house_number'] = "-"
            jData['road'] = "-"
            jData['city'] = "-"
            jData['state'] = "-"
            jData['postcode'] = "-"
            jData['country'] = "-"

        # Get the names of tagged faces
        metadataFields = metadata.xmp_keys
        nameList = []
        for i in range(len(metadataFields)):
            # print metadataFields[i] + " " + str(metadata[metadataFields[i]].raw_value)
            if re.search(r'Name', metadataFields[i], re.IGNORECASE):
                # print metadataFields[i] + ": " + metadata[metadataFields[i]].raw_value
                nameSplit = metadata[metadataFields[i]].raw_value
                nameSplit = nameSplit.split(": ")
                # print nameSplit
                name = nameSplit[0]
                bogusNames = ["Custom", "Medium Contrast"]
                if not re.search(r'^\.', name) and not name.endswith(tuple([".JPG", ".jpg", ".jpeg", ".JPEG"])) and not name in bogusNames and not re.search(r'NIKKOR', name) and not re.search(r'NIKON', name):
                    # Not ending in JPEG because we get the filename from this list in the pitc values sometimes. 
                    name = name.rstrip()
                    name = ' '.join([s[0].upper() + s[1:] for s in name.split(' ')])
                    nameList.append(name)
        jData['names'] = list(set(nameList))  ## De-duplicate names

        if 'Exif.Photo.UserComment' in metadata:
            autoTags = metadata['Exif.Photo.UserComment'].raw_value
            # autoTags = re.sub(r'charset=\"Ascii\"\s+', '', autoTags)
            if re.search(r'UUUUUUUU', autoTags):
                jData['autoTagsGoogle'] = []
                jData['autoTagsClarifai'] = []
            else:
                tagSplit = autoTags.split(', ')
                # print tagSplit
                autoTagsGoogList = []
                autoTagsClarList = []
                for tagOrig in tagSplit:
                    googVisionPrefix = params['params']['visionTaggingParams']['googleTagging']['googVisionLabelPrefix']
                    clarifaiPrefix = params['params']['visionTaggingParams']['clarifaiTagging']['clarifaiVisionLabelPrefix']
                    tag = re.sub(r'' + googVisionPrefix, '', tagOrig)
                    tag = re.sub(r'' + clarifaiPrefix, '', tag)
                    if re.search(r'_', tag):
                        try:
                            (comment, val) = tag.split('_')
                        except ValueError as ve:
                            logfile = open(os.path.join(script_path, 'tagSplitErrors.out'), 'a')
                            print >>logfile, 'Tag was ill-formed in file ' + str(filename) + ' ' + tag
                            continue
                        try:
                            comment = comment.decode('utf-8')
                        except UnicodeDecodeError as ude:
                            print comment
                            print "Unicode Error in this file: " + str(filename)

                            logfile = open(script_path + '/unicodeTagErrors.out', 'a')
                            print >>logfile, "Unicode Tag Error in this file: " + str(filename)
                            # exit(1)
                        tagPair = (comment, val)
                        if not (re.search('METADATA-START', tagOrig) or (tagOrig in nameList)):
                            # print tagPair[0]
                            if re.search(googVisionPrefix, tagOrig):
                                autoTagsGoogList.append(tagPair)
                            if re.search(clarifaiPrefix, tagOrig):
                                autoTagsClarList.append(tagPair)
                jData['autoTagsGoogle'] = autoTagsGoogList
                jData['autoTagsClarifai'] = autoTagsClarList
                # assert len(jData['autoTags']) > 0
                # assert not re.search(r'\\x[0-9a-f]{2}', str(autoTagsGoogList))
                # assert not re.search(r'\\x[0-9a-f]{2}', str(autoTagsClarifai))
                assert not re.search(r'googVision_', str(autoTagsGoogList))
                assert not re.search(r'clarifaiVision_', str(autoTagsClarList))
        else:
            jData['autoTagsGoogle'] = []
            jData['autoTagsClarifai'] = []

        if 'Iptc.Application2.Keywords' in metadata:
            picasaTags = metadata['Iptc.Application2.Keywords'].raw_value
            # tagSplit = picasaTags.split(',')
            pTags = []
            for tagOrig in picasaTags:
                if not (re.search('METADATA-START', tagOrig) or (tagOrig in nameList)):
                    pTags.append( (tagOrig, 1) )
            jData['picasaTags'] = pTags
            # assert len(jData['picasaTags']) > 0
        else:
            jData['picasaTags'] = []

        # print jData

        jsonObj = json.dumps(jData)
        # print jsonObj
        assert re.search(r'...............', jsonObj)
        # assert not re.search(r'\\x\d+', jsonObj)
        # assert not re.search(r'\\u[0=9a-f]{4}', jsonObj)
        return jsonObj



# image = sys.argv[1]
# print getExifData(image, True)


# proxy = xmlrpclib.ServerProxy("http://127.0.0.1:" + "8040" + "/RPC2")

# # val = json.loads(proxy.geoLookup("40.2338", "-111.6585").encode('utf-8'))

if __name__ == '__main__':

    if False:
        rootDirectory = "/home/lewis/Pictures"

        print rootDirectory
        for root, dir, file in os.walk(rootDirectory):
            print dir
            for file in os.listdir(root):
                fullPath =  os.path.join(root, file)
                print getExifData(fullPath, True)
    else:
        fullPath = "/mnt/NAS/Jessica Pictures/Laptop/Peru/Uros Islands/Other/20160502_104348.jpg"
        print getExifData(fullPath, True)



    if True:
        # testImage = "/home/lewis/Pictures/chicago_sept (3).jpg"
        testImage = "/home/lewis/test.jpg"

        metadata = pyexiv2.ImageMetadata(testImage)
        try:
            metadata.read()
        except IOError as ioe:
            print str(ioe)
            exit(1)

        metadataFields = metadata.exif_keys
        nameList = []
        # print "here"
        print metadataFields
        for i in range(len(metadataFields)):
            # print metadataFields[i]
            print metadataFields[i] + " " + str(metadata[metadataFields[i]].raw_value)
            if (re.search('Date', str(metadata[metadataFields[i]].raw_value))):
                print "found"
                print metadataFields[i] + " " + str(metadata[metadataFields[i]].raw_value)
    # print getExifData(testImage, False)
# else:

#     dirFile = open(script_path + "/directories.txt", 'r')
#     directories = dirFile.read().splitlines()
#     for curDir in directories:
#         print curDir
#         for filenames in os.listdir(curDir):
#             fullPath = os.path.join(curDir, filenames)
#             print fullPath
#             print getExifData(fullPath, True)
#             for fname in filenames:
#                 if fname.endswith(tuple([".JPG", ".jpg", ".jpeg", ".JPEG"])):
#                     filename = os.path.join(dirpath, fname)
#                     # getExifData(filename, False)
#                     print filename
