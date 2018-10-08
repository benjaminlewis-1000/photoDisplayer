#! /usr/bin/env python

import subprocess 
from subprocess import PIPE
from time import sleep
import signal
import os
import threading
import Queue

class fehManager():

    def __init__(self):
        self.fehExe = None
        self.file = '/app/ssList.tmp'
        self.commands = ['-FxZNzY', '-D 4', '--auto-rotate']
        self.errQueue = Queue.Queue()
        self.__readExeOut__()

    def setParams(self, commands):
        self.commands = commands

    def setFile(self, fileName):
        self.file = fileName

    def start(self):
        if self.fehExe is None:
            self.__startExe__()
        else:
            self.__killExe__()
            self.__startExe__()
    
    def stop(self):
        self.__killExe__()

    def __killExe__(self):
        if self.fehExe is not None:
            self.fehExe.terminate()
            self.fehExe.wait()
            self.fehExe = None
            sleep(3)

    def __startExe__(self):
        print "Starte exe"
        self.fehExe = subprocess.Popen(['/usr/local/bin/feh'] + self.commands + ['-f', self.file], stderr = PIPE, stdout = PIPE)
        print "Done launching!"
        self.__watchdog__()

    def __readExeOut__(self):
        # print 'hey'
        if self.fehExe is not None:
            try:
                stderr = self.fehExe.stderr.readline()
                print stderr
                self.errQueue.put(stderr)
            except Exception as e:
                pass
        else:
        #    print "no exe"
            pass 
        threading.Timer(3, self.__readExeOut__).start()

    def __watchdog__(self):
        # print "watchdog"
        if self.fehExe is None:
            threading.Timer(5, self.__watchdog__).start()
        else:
            if not self.errQueue.empty():
                err = self.errQueue.get()
                if "X Error of failed" in err or "Major opcode" in err:
                    self.__killExe__()
                    self.__startExe__()
            else:
                pass
            threading.Timer(5, self.__watchdog__).start()


