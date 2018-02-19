#! /usr/bin/env python 

## Screen client

import xmlrpc.client

class screenClient():
    
    def __init__(self):
        self.proxy = xmlrpc.client.ServerProxy('http://127.0.0.1:8543/')
        
    def toggleScreen(self):
        self.proxy.toggleScreen()
        
    def turnOnScreen(self):
        self.proxy.turnOnScreen()
        
    def turnOffScreen(self):
        print self.proxy.turnOffScreen()
        
    def askForTvOn(self, time):
        print self.proxy.askForTvOn(time)

if __name__ == "__main__":
    sc = screenClient()
    # sc.askForTvOn(40)
    sc.turnOffScreen()
