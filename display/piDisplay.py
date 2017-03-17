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

stream = open("/home/pi/photoDisplayer/config/params.yaml", "r")
params = yaml.load(stream)

# if (sys.platform )
print sys.platform
# Get current OS
osRegex = re.search('.*nux.?', sys.platform)
# currentOS
if (osRegex == None): # Windows
    osRegex = re.search('.*win.?', sys.platform)
    if (osRegex.group(0)):
        currentOS = params['windowsType']
    else:
        # MAC, not defined
        currentOS = 0
else:
    currentOS = params['linuxType']


# Connect to the database
conn = sqlite3.connect(rootDir + "/databases/" + params['database'])
conn.text_factory = str  # For UTF-8 compatibility

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

query = "SELECT " + params['photoFileColumn'] + ", " + params['rootDirNumColumn'] + ", " + params['photoDateColumn'] + " FROM " + params['photoTableName'] + " WHERE " + params['photoYearColumn'] + " = ?" + " AND " + params['photoMonthColumn'] + " = ?"
val = (2016, 6)

query = "SELECT photo_file, root_dir_num, photo_date from photos where photo_key in (SELECT photo from Linker where person = 4 OR person = ?)"
print query
val = (5,)
f1=open('testfile', 'w+')
f1.write('This is a test')
# sleep(6)


valid_photos = []
photo_dates = []

photo_file = open('/tmp/photos.txt', 'w') # Overwrite the existing file at that location.

for row in c.execute(query, val):
    # print row
    filename = rootDirs[row[1]] + row[0]
    # print filename
    # print row[2]
    f1.write((row[2] + " " + filename + "\n"))
    valid_photos.append(filename)
    photo_dates.append(row[2])
    photo_file.write(filename + "\n")

photo_file.close()

p1 = subprocess.Popen(["feh", "-YFxZNz", "-D", "2", "--auto-rotate", "-d", "-f", "/tmp/photos.txt"])

# arg_list =  ' '.join(valid_photos)
# prevPicNum = 0
# picNum = 0
# print valid_photos[0]
# while 1:
#     while (picNum == prevPicNum):
#         picNum = random.randint(0, len(valid_photos) - 1)
#     prevPicNum = picNum
#     picture = valid_photos[picNum]
#     p1 = subprocess.Popen(["feh", "-F", valid_photos[picNum]])
#     print photo_dates[picNum] + " " + valid_photos[picNum]
#     sleep(5)
