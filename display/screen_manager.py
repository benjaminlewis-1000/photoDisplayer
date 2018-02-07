#! /usr/bin/env python

import subprocess
import shlex
import re
import thread
import Queue
import sys
import termios
import pexpect
import threading
from time import sleep
import time
import os

class tvStateManager():

    def __init__(self):
        
        self.process = pexpect.spawn('cec-client')
        
        self.commandQueue = Queue.Queue()
        self.cecQueue = Queue.Queue()
        self.powerQueue = Queue.Queue()
        self.activeQueue = Queue.Queue()
        
        self.powerQueue.put('unknown')
        self.activeQueue.put('unknown')
        self.powerState = 'off'
        self.activeState = 'unknown'
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.safeToDetermineState = False

        self.stateSafeSemaphore = threading.Condition()
        
        thread.start_new_thread(self.__tv_state_monitor__, () )
        thread.start_new_thread(self.__command_reader__, (self.process,) )
        thread.start_new_thread(self.__cec_output_consumer__, (self.process,) )
        self.__determine_unknown_state__()
        
    def __determine_unknown_state__(self):
        sleep(5)
        computerState = self.computerIsActive()
        powerState = self.tvIsOn()
        # Sleep 10 seconds if necessary
        if computerState == 'raspi' or computerState == 'not_raspi':
            return # We have our answer 
        if powerState == 'on' or powerState == 'unknown': 
            # Don't want to mess with currently powered on TV - either it's
            # on the right input already or we don't want to hijack the TV from someone. 
            threading.Timer(5, self.__determine_unknown_state__).start()
        else: # Power is off
            if powerState == 'off':
                imgname = os.path.join(self.dir_path, 'dontpanic.png')
                imshow = subprocess.Popen(['/usr/local/bin/feh', '-ZxF', imgname]) 
                self.process.sendline('as')

                safeState = False
                while not safeState:
                    sleep(2)
                    self.stateSafeSemaphore.acquire()
                    safeState = self.safeToDetermineState 
                    self.stateSafeSemaphore.release()
                    print "State safety in loop is {}".format(safeState)

                computerState = self.computerIsActive()
                if computerState == 'raspi' :
                    print "Computer state is known as raspi"
                    self.process.sendline('standby 0')

                if computerState == 'raspi' or computerState == 'not_raspi':
                    imshow.terminate()
                    return
                else:
                    print "Try, try again"
                    print "Computer state is {}, power state is {}".format(computerState, powerState)
                    # Try, try again
                    threading.Timer(5, self.__determine_unknown_state__).start()
                
            else:  # Shoot, someone turned the TV back on. Try again later. 
                # Try, try again
                threading.Timer(5, self.__determine_unknown_state__).start()
                        
    def __cec_output_consumer__(self, process):
        # This thread will block, but that's OK because the only thing it does is 
        # consume and put on the queue
        while 1:
            try:
                stdout = self.process.readline()
                stdout = stdout.lower().rstrip()
                self.cecQueue.put(stdout)
                #print stdout 
            except pexpect.exceptions.TIMEOUT:
                pass
    
    def __command_reader__(self, process):
        # Only reads off data from the cec process, since it will block if there
        # is no new data
        while 1:
            
            # Workaround to check if the queue is empty - see if there is
            # something to read with a nonblocking call   
                    
            if not self.commandQueue.empty() :
                
                ## sleep(5)  # Wait a bit - cec-client takes a little while to update to current state, sometimes.
                powerState = self.tvIsOn()
                activeState = self.computerIsActive()
                
                command = self.commandQueue.get(False)
                if command == 'toggle' and activeState == 'raspi':
                    if powerState == 'on':
                        string = 'off'                    
                    else:
                        string = 'on'
                    print "Command toggle received in thread - turning {}".format(string)
                    if powerState == 'on':
                        while powerState == 'on':
                            self.process.sendline('standby 0')
                            sleep(5)
                            powerState = self.tvIsOn()
                            
                        # echo on 0
                    else:
                        while powerState == 'off':
                            self.process.sendline('as')
                            sleep(5)
                            powerState = self.tvIsOn()
                    # Toggle screen
                elif command == 'turnOn' and powerState == 'off':
                    print "Command turnon received in thread - turning on"
                    while powerState == 'off':
                        self.process.sendline('as')
                        sleep(5)
                        powerState = self.tvIsOn()
                    # Else, don't change anything
                    # Turn on the screen if not on something else
                elif command == 'turnOff' and activeState == 'raspi':
                    print "Command turnoff received in thread - turning off"
                    while powerState == 'on':
                        self.process.sendline('standby 0')
                        sleep(5)
                        powerState = self.tvIsOn()
                    # Turn off the screen if raspi is active
                else:
                    # Not in the right state or the command isn't valid
                    print 'Rejecting command because TV is not on computer input'
                        
    def __tv_state_monitor__(self):

        lastRead = time.time()
        while 1:
            if not self.cecQueue.empty():
                lastRead = time.time()
                self.stateSafeSemaphore.acquire()
                self.safeToDetermineState = False
                self.stateSafeSemaphore.release()
                stdout = self.cecQueue.get()
                
                if re.match(".*?power status changed.*to 'on'.*?", stdout):
                    # print "Power turned on"
                    # Clear the queue
                    while not self.powerQueue.empty():
                        self.powerQueue.get()
                    # Put the latest state in the queue
                    self.powerQueue.put('on')
                    
                elif re.match(".*?power status changed.*to 'standby'.*?", stdout):
                    # print "Power turned off"
                    # Clear the queue
                    while not self.powerQueue.empty():
                        self.powerQueue.get()
                    # Put the latest state in the queue
                    self.powerQueue.put('off')
                    
                elif re.match(".*?making tv.*the active source.*?", stdout):
                    print "raspi is not the active source"
                    # Clear the queue
                    while not self.activeQueue.empty():
                        self.activeQueue.get()
                    # Put the latest state in the queue
                    print "Putting not_raspi"
                    self.activeQueue.put('not_raspi')
                elif re.match(".*?making recorder.* the active source.*?", stdout):
                    print "raspi is the active source"
                    # Clear the queue
                    while not self.activeQueue.empty():
                        self.activeQueue.get()
                    # Put the latest state in the queue
                    print "Putting raspi"
                    self.activeQueue.put('raspi')
            else:
                if (time.time() - lastRead) == 2:
                    self.stateSafeSemaphore.acquire()
                    self.safeToDetermineState = True
                    print "safe to determine state"
                    self.stateSafeSemaphore.release()
                    
    def tvIsOn(self):
        self.stateSafeSemaphore.acquire()
        safeState = self.safeToDetermineState 
        self.stateSafeSemaphore.release()

        print "State safety is {}".format(safeState)
        if not self.powerQueue.empty() and safeState :
            self.powerState = self.powerQueue.get()
        # If nothing has changed, the queue will be empty and the state 
        # won't have changed
            
        return self.powerState 
                
    def computerIsActive(self):

        self.stateSafeSemaphore.acquire()
        safeState = self.safeToDetermineState 
        self.stateSafeSemaphore.release()

        print "State safety is {}".format(safeState)

        if not self.activeQueue.empty() and safeState:
            self.activeState = self.activeQueue.get()
        # If nothing has changed, the queue will be empty and the state 
        # won't have changed
            
        return self.activeState
                  
    def toggleScreen(self):
        self.commandQueue.put('toggle', False)
        pass
        
    def turnOnScreen(self):
        self.commandQueue.put('turnOn', False)
        
    def turnOffScreen(self):
        self.commandQueue.put('turnOff', False)
        
    def askForTvOn(self, nextNSeconds):
        sleep(5)
        activeState = self.computerIsActive()
        powerState = self.tvIsOn()
        
        if powerState == 'on' and activeState == 'raspi':
            # Good, we're in the state we need to be in. 
            # Turn it off in nextNSeconds seconds
            "TV is already on"
            self.turnOnScreen()
            threading.Timer(nextNSeconds, self.turnOffScreen).start()
        elif activeState != 'raspi' and powerState == 'on':
            # Not on the raspberry pi and TV is on
            # Wait a minute and try again
            waitTime = 10
            print "Can't turn TV on, not active source"
            threading.Timer(waitTime, self.askForTvOn, [nextNSeconds - waitTime]).start()
        else: #  powerState == 'off'
            print "Turning on TV as asked for"
            self.turnOnScreen()
            threading.Timer(nextNSeconds, self.turnOffScreen).start()
        
if __name__ == "__main__":  
    ccl = tvStateManager()

    while 1:
        sys.stdout.flush()
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        filename = raw_input()
        if filename.lower() == 'on':
            ccl.turnOnScreen()
        elif filename.lower() == 'toggle':
            ccl.toggleScreen()
        elif filename.lower() == 'off':
            ccl.turnOffScreen()
        elif filename.lower() == 'askon':
            ccl.askForTvOn(60)


