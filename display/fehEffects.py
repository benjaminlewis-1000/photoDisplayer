#! /usr/bin/env python

import os
import sys
from PIL import Image

rootDir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
deleteFile = os.path.join(rootDir, 'delete_these_paths.out')
alterFile = os.path.join(rootDir, 'altered_paths.out')

assert len(sys.argv) == 3

filename = sys.argv[1]
fehNumber = sys.argv[2]

# assert os.path.isfile(str(filename)), 'File {} input is not a file'.format(filename)

img = Image.open(filename)

def rotate_clockwise(img, filename):
	with open(alterFile, 'a') as fh:
		print >>fh, 'Image {} was rotated clockwise'.format(filename)
	img = img.rotate(270, expand=True)
	img.save(filename)

def rotate_counterclockwise(img, filename):
	with open(alterFile, 'a') as fh:
		print >>fh, 'Image {} was rotated counterclockwise'.format(filename)
	img = img.rotate(90, expand=True)
	img.save(filename)

def rotate_180(img, filename):
	with open(alterFile, 'a') as fh:
		print >>fh, 'Image {} was rotated 180 degrees'.format(filename)
	img = img.rotate(180, expand=True)
	img.save(filename)

def mark_for_deletion(img, filename):
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
    print func(img, filename)

numbers_to_months(fehNumber)
