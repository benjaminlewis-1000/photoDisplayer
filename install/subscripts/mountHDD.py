#! /usr/bin/env python

import Tkinter, Tkconstants, tkFileDialog
from Tkinter import *

piRootDir = '/media/pi'

root = Tk()
root.filename = tkFileDialog.askdirectory(initialdir = piRootDir)

print root.filename

