#! /usr/bin/python


import argparse


parser = argparse.ArgumentParser(description='Tag images using the Clarifai vision API (see clarifai.com). Inputs can include a directory; otherwise, a pop-up window will ask for a root directory to scan.')
parser.add_argument('--root', help='Root directory of the images to scan.')
parser.add_argument('--doDeep', help="Doesn't use the indexed files in the database to skip already read files; tends to run slower.")
parser.add_argument('--method', help="Select methods. Valid values currently are 'google' or 'clarifai'.")

args = parser.parse_args()

if args.method == 'clarifai':
	method = 'clarifai'
else:
	method = 'google'

print method