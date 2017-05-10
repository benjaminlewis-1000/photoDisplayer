#! /usr/bin/python


import os
import time

start = time.time()

dir = 'N:\Photos\\2016\\'

directories = []

for dirpath, dirnames, filenames in os.walk(dir):
	print dirpath
	directories.append(dirpath)
	# for fname in filenames:
	# 	if fname.endswith(tuple(ext)):
	# 		listAllFiles.append(os.path.join(dirpath, fname))

end = time.time()

print end - start