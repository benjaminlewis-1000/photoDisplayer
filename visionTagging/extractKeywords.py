#! /usr/bin/env python

import operator
import re

fname = 'logLandmarks.out'

wordDict = {}

with open(fname) as f:
    content = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content] 

for line in content:
	# print line
	# print ""
	match = re.search(r"{u'labelAnnotations': (\[.*?\])", line)
	if match:
		notations = match.group(1)
		keywords = re.finditer(r"u'description': u'(.*?)'", notations)
		for i in keywords:
			word = i.group(1)
			if word in wordDict:
				wordDict[word] = wordDict[word] + 1
			else:
				wordDict[word] = 1


# print wordDict
sorted_x = sorted(wordDict.items(), key=operator.itemgetter(1))
sorted_x.reverse()
# for i in range(len(sorted_x)):
# 	print sorted_x[i][0] + " : " + str(sorted_x[i][1])

with open('landmarkKeywords.txt', 'w') as f:
	for i in range(len(sorted_x)):
		if sorted_x[i][1] > 15:
			if sorted_x[i][0].strip() not in ['person', 'day', 'text', 'stage', 'room', 'people', 'snow', \
			   'season', 'wall', 'adventure', 'image', 'photograph', 'light', 'shape', 'lighting', 'water', 'vehicle', \
			   'night', 'sea', 'rock', 'tree']  :
				print >>f, sorted_x[i][0]
				print sorted_x[i][0] + " : " + str(sorted_x[i][1])
