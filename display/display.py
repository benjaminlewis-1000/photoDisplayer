#! /usr/bin/python

import sqlite3
import os
import yaml
import sys
import re
import random
import subprocess
from time import sleep

rootDir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

stream = open("/home/lewis/gitRepos/photoDisplayer/config/params.yaml", "r")
params = yaml.load(stream)

# if (sys.platform )
print sys.platform
osRegex = re.search('.*nux.?', sys.platform)
# currentOS
if (osRegex.group(0)):
    # We're working on Linux
    currentOS = params['linuxType']
else:
    osRegex = re.search('.*dows.?', sys.platform)
    if (osRegex.group(0)):
        currentOS = params['windowsType']
    else:
        # MAC, not defined
        currentOS = 0

# Connect to the database
conn = sqlite3.connect(rootDir + "/databases/photos_master.db")

c = conn.cursor()

# Get information on the root directories, put in this dict (like a hash)
rootDirs = {}

print 'windows' if currentOS == 1 else 'linux' + ' is your OS'
# columns = (params['rootKeyColumn'], \
#     params['linuxRootPath' if currentOS == params['linuxType'] else 'windowsRootPath'])#,\
    # params['rootTableName']
    # )
# print columns
query = "SELECT " + params['rootKeyColumn'] + ", " \
    + params['linuxRootPath' if currentOS == params['linuxType'] else 'windowsRootPath'] \
    +  " FROM " + params['rootTableName']
for row in c.execute(query):
    # print row
    rootDirs[row[0]] = row[1]

# Get a simple batch of photos, say all from root_dir = 1

query = "SELECT " + params['photoFileColumn'] + ", " + params['rootDirNumColumn'] + ", " + params['photoDateColumn'] + " FROM " + params['photoTableName'] + " WHERE " + params['photoDayColumn'] + " = ?"
val = (17,)
print query
f1=open('testfile', 'w+')
f1.write('This is a test')
# sleep(6)


valid_photos = []
photo_dates = []

for row in c.execute(query, val):
    # print row
    filename = rootDirs[row[1]] + row[0]
    # print filename
    # print row[2]
    f1.write((row[2] + " " + filename + "\n"))
    valid_photos.append(filename)
    photo_dates.append(row[2])

# val = '/home/lewis/Pictures/Family Pictures/2015/Fall 2015/_DSC0714.JPG'
# p1 = subprocess.Popen(["eog", "-w", val])


# sleep(10)
# print valid_photos    
print
print 
arg_list =  ' '.join(valid_photos)
prevPicNum = 0
picNum = 0
print valid_photos[0]
while 1:
    while (picNum == prevPicNum):
        picNum = random.randint(0, len(valid_photos) - 1)
    prevPicNum = picNum
    picture = valid_photos[picNum]
    p1 = subprocess.Popen(["feh", "-F", valid_photos[picNum]])
    print photo_dates[picNum] + " " + valid_photos[picNum]
    sleep(5)