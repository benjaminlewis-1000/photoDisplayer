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

stream = open(rootDir + "/config/params.yaml", "r")
params = yaml.load(stream)

# Get the platform
# print sys.platform
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

query = "SELECT " + params['personNameColumn'] +  " FROM " + params['peopleTableName']


valid_photos = []
photo_dates = []

people_file = open('people.txt', 'w') # Overwrite the existing file at that location.

people_list = []

for row in c.execute(query):
    people_list.append(row[0])

sorted_people = sorted(people_list, key=lambda s: s.lower())
print '\n'.join(sorted_people)
people_file.write(', '.join(sorted_people))
people_file.close()



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
