#! /usr/bin/env python

import os
import sys
# from PIL import Image
from subprocess import call

rootDir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
deleteFile = os.path.join(rootDir, 'delete_these_paths.out')
alterFile = os.path.join(rootDir, 'altered_paths.out')

assert len(sys.argv) == 3

filename = sys.argv[1]
fehNumber = sys.argv[2]

# assert os.path.isfile(str(filename)), 'File {} input is not a file'.format(filename)

def rotate_clockwise(filename):
	with open(alterFile, 'a') as fh:
		print >>fh, 'Image {} was rotated clockwise'.format(filename)
        call(['sudo', '/usr/bin/exiftran', filename, '-i9']) 

def rotate_counterclockwise(filename):
	with open(alterFile, 'a') as fh:
		print >>fh, 'Image {} was rotated counterclockwise'.format(filename)
        call(['sudo', '/usr/bin/exiftran', filename, '-i2']) 

def rotate_180(filename):
	with open(alterFile, 'a') as fh:
		print >>fh, 'Image {} was rotated 180 degrees'.format(filename)
        call(['sudo', '/usr/bin/exiftran', filename, '-i1']) 

def mark_for_deletion(filename):
	with open(deleteFile, 'a') as fh:
		print >>fh, filename

def numbers_to_months(argument):
    switcher = {
        'cw': rotate_clockwise,
        'ccw': rotate_counterclockwise,
        'r180': rotate_180,
        'del': mark_for_deletion
        # 4: four,
        # 5: five,
        # 6: six,
        # 7: seven,
        # 8: eight,
        # 9: nine,
        # 10: ten,
        # 11: eleven,
        # 12: twelve
    }
    # Get the function from switcher dictionary
    func = switcher.get(argument, lambda: "Invalid month")

    # Execute the function
    print switcher.get(argument)
    func(filename)

numbers_to_months(fehNumber)
