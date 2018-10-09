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

''' 
getExif is a function that retrieves, where avaliable, the following data from a JPEG image: 

'ISO8601' - ISO format date/time of the photo
'year' - the respective value from the ISO date
'month' - the respective value from the ISO date
'day' - the respective value from the ISO date
'hour' - the respective value from the ISO date
'min' - the respective value from the ISO date
'sec' - the respective value from the ISO date
'TimeZone' - the respective value from the ISO date

'latitude' - lat of the photo, if set
'longitude' - lon of the photo, if set

'house_number' - decoded from lat/lon if doGeocode is set to "True"
'road' - decoded from lat/lon if doGeocode is set to "True"
'city' - decoded from lat/lon if doGeocode is set to "True"
'state' - decoded from lat/lon if doGeocode is set to "True"
'postcode' - decoded from lat/lon if doGeocode is set to "True"
'country' - decoded from lat/lon if doGeocode is set to "True"

'names' - a list of all names of people in the photo, de-duplicated
'picasaTags' - tags that are user-set, from Picasa
'autoTagsClarifai' - tags that were automatically assigned from Clarifai
'autoTagsGoogle' - tags that were automatically assigned from Google services

'''

def getExifData(filename, doGeocode):

    if filename.endswith(tuple([".JPG", ".jpg", ".jpeg", ".JPEG"])):
       
        # Read the exiv2 metadata from the image
        metadata = pyexiv2.ImageMetadata(filename)
        try:
            metadata.read()
        except IOError as ioe:
            print "IO Error in getExif.py: " +  str(ioe)
         #   exit(1)
            logfile = open(script_path + '/logBadMetadata.out', 'a')
            print >>logfile, str(ioe) + ": metadata error in " + filename 
            logfile.close()
            return "", ""
        dateOK = True
        # print metadata.keys()
        # print 'Exif.Photo.DateTimeOriginal' in metadata

        # Preferred fields: 'Exif.Photo.DateTimeOriginal' or 'Exif.Photo.DateTimeDigitized'
        # Retrieve the time from the EXIV
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
                        dateOrig = '1900:01:01 01:01:01'
                    # Don't need similar in the else clause below, because in that clause we know DTO isn't there.
                # print dateOrig
            else:
                dateOrig = metadata['Exif.Photo.DateTimeDigitized'].raw_value
            dateTime = dateOrig.split(" ")
            # print dateOrig
            # Error case - there is a valid field, but it contains no numbers. 
            if not re.search(r'[0-9]+:\d+:\d+', dateOrig) or re.search(r'0000:00:00 00:00:00', dateOrig):
                dateOK = False
                dateIso = "1900:01:01 01:01:01"
                dateTime = dateIso.split(" ")
            # print dateTime
            dateIso = dateTime[0].replace(":", "-") + " " +  dateTime[1]
        if not dateOK:
            print "Entering Date Taken Remediation. "
            ## Try to find an acceptable date - at least 'last edited.'
            dateIso = "1900-01-01 01:01:01"
            for key in metadata.keys():
                if re.search('date', key, re.IGNORECASE):
                    rawTime = metadata[key].raw_value
                    # print rawTime

                    if re.search(r'[0-9]+:\d+:\d+', rawTime):
                        dt = parser.parse(rawTime)
                        possVal = dt.isoformat().replace("T", " ")
                        if possVal  < dateIso:
                            dateIso = possVal

            dateTime = dateIso.split(" ")
            ## See if the file name is any good:
            file_name_string = filename.split('/')[-1].split('\\')[-1]

            for ending in tuple([".JPG", ".jpg", ".jpeg", ".JPEG"]):
                file_name_string = file_name_string.replace(str(ending), "")

            # Common format seems to be yyyy-mm-dd hh.mm.ss
            file_name_string = file_name_string.replace('.', ':')
            file_name_string = file_name_string.replace('-', ':')

            try:
                dt = parser.parse(file_name_string)
                possVal = dt.isoformat().replace("T", " ")
                if possVal < dateIso:
                    dateIso = possVal
            except ValueError as ve:
                pass
                # No discernible date.

            # print "DateISO is " + dateIso

            # print metadata
            print "Changing date to: " + str(dateIso)
            sleep(0.3)
            metadata['Exif.Photo.DateTimeOriginal'] = dateIso
            metadata.write()

            logfile = open(script_path + '/logNoDates.out', 'a')
            try:
                utf_filename = filename.encode('utf-8')
            except UnicodeDecodeError as ude:
                utf_filename = filename
                logfile = open(script_path + '/unicodeTagErrors.out', 'a')
                print >>logfile, "Unicode Date Error in this file: " + str(utf_filename)
            print >>logfile, "Date/time for: " + utf_filename + " modified."
            logfile.close()

            # if __name__ == "__main__":
            #     return -1, -1
            # else:
            #     return -1

        print dateTime
        assert len(dateTime) == 2  # Date and time
        assert len(dateTime[0]) == 10 # Date is of format YYYY:MM:DD
        assert len(str(dateTime[1])) == 8 or len(str(dateTime[1])) == 14
        # Date time parser - python library
        dt = parser.parse(dateIso)

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
            # Get the latitude/longitude and N/S and E/W
            northSouth = metadata['Exif.GPSInfo.GPSLatitudeRef'].raw_value
            eastWest = metadata['Exif.GPSInfo.GPSLongitudeRef'].raw_value
            lat = str(metadata['Exif.GPSInfo.GPSLatitude'].raw_value)
            lon = str(metadata['Exif.GPSInfo.GPSLongitude'].raw_value)
            latSplit = lat.split(" ")
            lonSplit = lon.split(" ")
            assert len(latSplit) == 3
            assert len(lonSplit) == 3
            # Compute the latitude and longitude in decimal form
            latDec = 1.0 * eval(latSplit[0] + '.0') + 1.0/60.0 * eval(latSplit[1] + '.0') + 1.0/3600.0 * eval(latSplit[2] + '.0')
            lonDec = 1.0 * eval(lonSplit[0] + '.0') + 1.0/60.0 * eval(lonSplit[1] + '.0') + 1.0/3600.0 * eval(lonSplit[2] + '.0')

            if (northSouth != "N"):
                latDec *= -1.0
            if (eastWest != "E"):
                lonDec *= -1.0

            jData['latitude'] = latDec
            jData['longitude'] = lonDec

            if doGeocode:
                # Do a reverse geocode lookup using the geoServer.py server, which is started by addPics.py
                proxy = xmlrpclib.ServerProxy("http://127.0.0.1:" + params['params']['serverParams']['geoServerPort'] + "/RPC2")
                try:
                    val = proxy.geoLookup(latDec, lonDec)
                    if val == -1:
                        if __name__ == "__main__":
                            return -1, -1
                        else:
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
        # nameList = []
        # print metadataFields

        # There are two different ways of storing names in XMP data, so I do 
        # both of them and join them in a set list.
        regionlist_name_regex = re.compile('.*RegionList.*Name.*')
        nameKeys = filter(regionlist_name_regex.match, metadata.keys())
        nameList = [metadata[nk].value for nk in nameKeys]
        # Take out the JPEG filenames in the 'name' list - happens sometimes apparently.
        jpeg_regex = re.compile('.*JPE?G$', re.IGNORECASE)
        jpeg_list = filter(jpeg_regex.search, nameList)
        # Also takes out some bogus names...
        nameList = set(nameList) - set(jpeg_list) - set(["Custom", "Medium Contrast"])
        # print nameList

        # for i in range(len(metadataFields)):
        #     # Find all fields that have the word 'name' in them, regardless of case. 
        #     if re.search(r'Name', metadataFields[i], re.IGNORECASE):
        #         nameSplit = metadata[metadataFields[i]].raw_value
        #         nameSplit = nameSplit.split(": ")
        #         name = nameSplit[0]
        #         bogusNames = ["Custom", "Medium Contrast"]
        #         if not re.search(r'^\.', name) and not name.endswith(tuple([".JPG", ".jpg", ".jpeg", ".JPEG"])) and not name in bogusNames and not re.search(r'NIKKOR', name) and not re.search(r'NIKON', name):
        #             # Not ending in JPEG because we get the filename from this list in the pitc values sometimes. 
        #             name = name.rstrip()
        #             name = ' '.join([s[0].upper() + s[1:] for s in name.split(' ')])
        #             nameList.append(name)
        # print nameList
        jData['names'] = list(nameList) # .union(set(nameList)))  ## De-duplicate names

        if 'Exif.Photo.UserComment' in metadata:
            autoTags = metadata['Exif.Photo.UserComment'].raw_value
            # autoTags = re.sub(r'charset=\"Ascii\"\s+', '', autoTags)
            if re.search(r'UUUUUUUU', autoTags):
                # Reject a tag that has been shown to have a erroneous value in these fields.
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

        # Don't process pictures that are tagged as 'exclude'
        picTagStrings = [val[0].lower() for val in jData['picasaTags']]
        if set(['exclude', 'ignore', 'remove']).intersection(set(picTagStrings)) != set([]):
            if __name__ == "__main__":
                return -1, -1
            else:
                return -1

        jsonObj = json.dumps(jData)
        assert re.search(r'...............', jsonObj)
        # print __name__
        if __name__ == "__main__":
            return jsonObj, metadata
        else:
            return jsonObj


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
        fullPath = "D:\\Pictures\\Emily's Pictures\\3-30-2009\\DSCN0456.JPG"
        fullPath = 'D:\Pictures\\2016\Provo\july_4_parade (22).JPG'
        fullPath = '/home/lewis/test_imgs/test2.jpg'
        fullPath = '/home/lewis/test_imgs/DSC_9833.JPG'
        fullPath = '/photos/Photos/Pictures_finished/2017/Family Texts/2017-12-01 19.40.11-4.jpg'
        fullPath = 'S:\\Photos\\Pictures_Jessica\\Family Scans\\2006\\july_2006 0012.jpg'
        fullPath = 'C:\\Users\\Benjamin\\Dropbox\\Camera Uploads\\2018-09-16 07.38.35.jpeg'
        fullPath = '/photos/Photos/Pictures_In_Progress/2018/Baby Announcements/DSC_5458.JPG'
        # print fullPath
        fullPath = '/photos/Photos/Pictures_In_Progress/2018/Babymoon/Italy/Rachel Pictures/IMG_3118.jpg'
        jsonObj, metadata = getExifData(fullPath, False)
        print jsonObj

        # for i in range(len(metadata.xmp_keys)):
        #   try:
        #     print metadata.xmp_keys[i] + ": " + str(metadata[metadata.xmp_keys[i]].value)
        #   except Exception:
        #     print metadata.xmp_keys[i] + ": NA"

        # aa = pyexiv2.xmp.XmpTag
        # metadata['Xmp.mwg-rs.Regions'] 
        # metadata.write()

        # for i in range(len(metadata.xmp_keys)):
        #   try:
        #     print metadata.xmp_keys[i] + ": " + str(metadata[metadata.xmp_keys[i]].value)
        #   except Exception:
        #     print metadata.xmp_keys[i] + ": NA"




    if False:
        # testImage = "/home/lewis/Pictures/chicago_sept (3).jpg"
        testImage = "D:\Pictures\Emily's Pictures\3-30-2009\4-27-08 403.jpg"

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
