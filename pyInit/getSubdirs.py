#! /usr/bin/env python

import os
import re
import pprint
# rootDir = "/home/lewis/gitRepos/photoDisplayer"
# rootDir2 = "/home/lewis/gitRepos/photoDisplayer/.git"
rootDir = "/home/lewis/gitRepos/photoDisplayer/history_js/vendor"
rootDir2 = "/home/lewis/gitRepos/photoDisplayer/history_js/scripts"
rootDir3 = "/home/lewis/gitRepos/photoDisplayer/history_js"

rrs = [rootDir3, rootDir2, rootDir]


def isSubDir(compDir, possibleSubDir):
    # print compDir
    # print possibleSubDir
    if re.search(r''+compDir, possibleSubDir) is None:
        return False
    else:
        return True




unq = getUniqueSubDirs(rrs)
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(unq)  
# subdirs1 = []
# for root, dirs, files in os.walk(rootDir):
#     subdirs1.append(root)

# subdirs2 = []
# for root, dirs, files in os.walk(rootDir2):
#     subdirs2.append(root)

# uniq = list(set(subdirs1) - set(subdirs2))
# for i in uniq:
#     print i